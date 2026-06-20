"""Движок генерации документов: рендер .docx (docxtpl) и конвертация в .pdf (LibreOffice)."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from docxtpl import DocxTemplate


def render_docx(template_path: str | Path, context: dict, output_path: str | Path) -> Path:
    """Рендерит .docx-шаблон с подстановкой context, сохраняет в output_path."""
    template_path = Path(template_path)
    output_path = Path(output_path)

    if not template_path.exists():
        raise FileNotFoundError(f'Шаблон не найден: {template_path}')

    output_path.parent.mkdir(parents=True, exist_ok=True)

    tpl = DocxTemplate(template_path)
    tpl.render(context)
    tpl.save(output_path)

    return output_path


def convert_to_pdf(docx_path: str | Path, output_dir: str | Path | None = None) -> Path:
    """Конвертирует .docx в .pdf через LibreOffice headless. Возвращает путь к PDF."""
    docx_path = Path(docx_path)

    if not docx_path.exists():
        raise FileNotFoundError(f'Файл не найден: {docx_path}')

    libreoffice = _find_libreoffice()
    if libreoffice is None:
        raise EnvironmentError(
            'LibreOffice не найден. Установите LibreOffice или запустите через Docker.'
        )

    if output_dir is None:
        output_dir = docx_path.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Конвертируем во временную папку, чтобы избежать конфликтов при параллельных запросах
    with tempfile.TemporaryDirectory() as tmp:
        # Отдельный профиль LibreOffice на каждый запуск: иначе параллельные
        # процессы (несколько воркеров gunicorn) конфликтуют за общий lock-файл
        # в ~/.config/libreoffice и второй процесс падает.
        user_profile = Path(tmp) / 'lo_profile'
        result = subprocess.run(
            [
                libreoffice,
                f'-env:UserInstallation=file://{user_profile}',
                '--headless', '--convert-to', 'pdf', '--outdir', tmp, str(docx_path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f'LibreOffice вернул ошибку: {result.stderr}')

        tmp_pdf = Path(tmp) / (docx_path.stem + '.pdf')
        if not tmp_pdf.exists():
            raise RuntimeError(f'PDF не создан. stdout: {result.stdout} stderr: {result.stderr}')

        output_pdf = output_dir / tmp_pdf.name
        shutil.move(str(tmp_pdf), str(output_pdf))

    return output_pdf


def _find_libreoffice() -> str | None:
    """Возвращает путь к исполняемому файлу LibreOffice или None."""
    for cmd in ('libreoffice', 'soffice', '/usr/bin/libreoffice', '/usr/bin/soffice'):
        if shutil.which(cmd):
            return cmd
    return None


def libreoffice_available() -> bool:
    """Публичная проверка доступности LibreOffice для конвертации в PDF."""
    return _find_libreoffice() is not None
