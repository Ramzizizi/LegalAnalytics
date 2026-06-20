import shutil
import subprocess
from unittest import mock

import pytest
from pathlib import Path
from django.conf import settings

from apps.templates_engine.services import (
    render_docx, convert_to_pdf, _find_libreoffice, libreoffice_available,
)


TEMPLATE_PATH = settings.WORD_TEMPLATES_DIR / 'dogovor_uslug.docx'

TEST_CONTEXT = {
    'number': '007/2025',
    'data': '19.06.2025',
    'contragent_name': 'ООО «Тест»',
    'contragent_director': 'Тестов Т.Т.',
    'contragent_inn': '7707083893',
    'contragent_kpp': '770701001',
    'contragent_address': 'г. Ростов-на-Дону, ул. Пушкина, д. 10',
    'executor_name': 'ООО «Исполнитель»',
    'lawyer_name': 'Юристов Ю.Ю.',
    'services_description': 'правовое консультирование',
    'summa': '50 000,00',
    'summa_words': 'пятьдесят тысяч рублей 00 копеек',
    'payment_days': '3',
    'date_start': '19.06.2025',
    'date_end': '19.12.2025',
}


@pytest.fixture
def output_dir(tmp_path):
    return tmp_path / 'output'


class TestRenderDocx:
    def test_шаблон_существует(self):
        assert TEMPLATE_PATH.exists(), f'Шаблон отсутствует: {TEMPLATE_PATH}'

    def test_создаёт_файл(self, output_dir):
        out = output_dir / 'result.docx'
        result = render_docx(TEMPLATE_PATH, TEST_CONTEXT, out)
        assert result == out
        assert out.exists()
        assert out.stat().st_size > 0

    def test_подставляет_значения(self, output_dir):
        """Проверяем, что теги заменены: открываем docx как zip и ищем значения в XML."""
        import zipfile
        out = output_dir / 'result.docx'
        render_docx(TEMPLATE_PATH, TEST_CONTEXT, out)

        with zipfile.ZipFile(out) as z:
            content = z.read('word/document.xml').decode('utf-8')

        assert 'ООО' in content
        assert '007/2025' in content
        assert '19.06.2025' in content
        # Теги {{ }} не должны остаться в документе
        assert '{{' not in content

    def test_ошибка_если_шаблон_не_существует(self, output_dir):
        with pytest.raises(FileNotFoundError):
            render_docx('/несуществующий/путь/template.docx', {}, output_dir / 'out.docx')

    def test_создаёт_вложенные_директории(self, tmp_path):
        nested = tmp_path / 'a' / 'b' / 'c' / 'result.docx'
        render_docx(TEMPLATE_PATH, TEST_CONTEXT, nested)
        assert nested.exists()


@pytest.mark.skipif(
    _find_libreoffice() is None,
    reason='LibreOffice не установлен (запустите в Docker для теста PDF)'
)
class TestConvertToPdf:
    def test_создаёт_pdf(self, output_dir):
        docx = output_dir / 'input.docx'
        render_docx(TEMPLATE_PATH, TEST_CONTEXT, docx)

        pdf = convert_to_pdf(docx, output_dir)
        assert pdf.exists()
        assert pdf.suffix == '.pdf'
        assert pdf.stat().st_size > 0

    def test_pdf_в_указанной_директории(self, output_dir):
        docx = output_dir / 'input.docx'
        render_docx(TEMPLATE_PATH, TEST_CONTEXT, docx)

        target = output_dir / 'pdfs'
        pdf = convert_to_pdf(docx, target)
        assert pdf.parent == target

    def test_ошибка_если_docx_не_существует(self, output_dir):
        with pytest.raises(FileNotFoundError):
            convert_to_pdf(output_dir / 'nope.docx')


class TestConvertToPdfMocked:
    """Тесты обработки ошибок конвертации без реального LibreOffice."""

    def test_ненулевой_returncode_кидает_runtimeerror(self, tmp_path):
        docx = tmp_path / 'input.docx'
        render_docx(TEMPLATE_PATH, TEST_CONTEXT, docx)

        fake = mock.Mock(returncode=1, stdout='', stderr='boom')
        with mock.patch('apps.templates_engine.services._find_libreoffice', return_value='soffice'), \
             mock.patch('apps.templates_engine.services.subprocess.run', return_value=fake):
            with pytest.raises(RuntimeError, match='boom'):
                convert_to_pdf(docx, tmp_path / 'out')

    def test_pdf_не_создан_кидает_runtimeerror(self, tmp_path):
        docx = tmp_path / 'input.docx'
        render_docx(TEMPLATE_PATH, TEST_CONTEXT, docx)

        # returncode=0, но файл PDF не появился во временной папке
        fake = mock.Mock(returncode=0, stdout='ok', stderr='')
        with mock.patch('apps.templates_engine.services._find_libreoffice', return_value='soffice'), \
             mock.patch('apps.templates_engine.services.subprocess.run', return_value=fake):
            with pytest.raises(RuntimeError, match='PDF не создан'):
                convert_to_pdf(docx, tmp_path / 'out')

    def test_libreoffice_отсутствует_кидает_environmenterror(self, tmp_path):
        docx = tmp_path / 'input.docx'
        render_docx(TEMPLATE_PATH, TEST_CONTEXT, docx)

        with mock.patch('apps.templates_engine.services._find_libreoffice', return_value=None):
            with pytest.raises(EnvironmentError):
                convert_to_pdf(docx, tmp_path / 'out')

    def test_libreoffice_available_возвращает_bool(self):
        assert isinstance(libreoffice_available(), bool)
