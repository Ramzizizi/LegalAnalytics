"""
Команда для ручной проверки генерации документа end-to-end.
Использование: python manage.py test_generate
"""
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from apps.templates_engine.services import render_docx, convert_to_pdf, _find_libreoffice


ТЕСТОВЫЙ_КОНТЕКСТ = {
    'number': '001/2025',
    'data': '01.01.2025',
    'contragent_name': 'ООО «Ромашка»',
    'contragent_director': 'Иванова И.И.',
    'contragent_inn': '7707083893',
    'contragent_kpp': '770701001',
    'contragent_address': 'г. Москва, ул. Ленина, д. 1',
    'executor_name': 'ООО «Юридическая помощь»',
    'lawyer_name': 'Петров П.П.',
    'services_description': 'юридическое сопровождение сделки',
    'summa': '150 000,00',
    'summa_words': 'сто пятьдесят тысяч рублей 00 копеек',
    'payment_days': '5',
    'date_start': '01.01.2025',
    'date_end': '31.12.2025',
}


class Command(BaseCommand):
    help = 'Тестовая генерация документа из шаблона dogovor_uslug.docx'

    def handle(self, *args, **options):
        template_path = settings.WORD_TEMPLATES_DIR / 'dogovor_uslug.docx'
        output_dir = settings.MEDIA_ROOT / 'test_output'

        self.stdout.write(f'Шаблон: {template_path}')

        # Генерация .docx
        docx_path = output_dir / 'test_dogovor.docx'
        render_docx(template_path, ТЕСТОВЫЙ_КОНТЕКСТ, docx_path)
        self.stdout.write(self.style.SUCCESS(f'✓ .docx создан: {docx_path}'))

        # Конвертация в .pdf
        if _find_libreoffice():
            pdf_path = convert_to_pdf(docx_path, output_dir)
            self.stdout.write(self.style.SUCCESS(f'✓ .pdf создан: {pdf_path}'))
        else:
            self.stdout.write(self.style.WARNING(
                '⚠ LibreOffice не найден — PDF-конвертация пропущена. '
                'Запустите через Docker для полной проверки.'
            ))

        self.stdout.write(self.style.SUCCESS('\nГенерация завершена успешно.'))
