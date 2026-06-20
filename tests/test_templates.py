"""Проверяем, что все 5 шаблонов рендерятся без незакрытых тегов."""
import zipfile
import pytest
from pathlib import Path
from django.conf import settings
from apps.templates_engine.services import render_docx

ШАБЛОНЫ_И_КОНТЕКСТЫ = [
    (
        'dogovor_uslug.docx',
        {
            'number': '001', 'data': '19.06.2025',
            'contragent_name': 'ООО Тест', 'contragent_director': 'Иванов',
            'contragent_inn': '7707083893', 'contragent_kpp': '770701001',
            'contragent_address': 'г. Москва', 'executor_name': 'ООО Исполнитель',
            'lawyer_name': 'Петров', 'services_description': 'услуги',
            'summa': '100000', 'summa_words': 'сто тысяч', 'payment_days': 5,
            'date_start': '01.01.2025', 'date_end': '31.12.2025',
        }
    ),
    (
        'dogovor_postavki.docx',
        {
            'number': '002', 'data': '19.06.2025',
            'contragent_name': 'ООО Покупатель', 'contragent_director': 'Сидоров',
            'contragent_inn': '7707083893', 'contragent_kpp': '770701001',
            'contragent_address': 'г. Москва', 'executor_name': 'ООО Поставщик',
            'lawyer_name': 'Кузнецов', 'tovar_naim': 'Кресло офисное',
            'tovar_kol': 10, 'tovar_price': '5000', 'tovar_summa': '50000',
            'summa_words': 'пятьдесят тысяч', 'delivery_date': '30.06.2025',
            'delivery_address': 'г. Москва, ул. Мира, 5', 'payment_days': 5,
        }
    ),
    (
        'pretenziya.docx',
        {
            'number': '003', 'data': '19.06.2025',
            'contragent_name': 'ООО Нарушитель', 'contragent_address': 'г. Москва',
            'contragent_inn': '7707083893', 'sender_name': 'ООО Пострадавший',
            'sender_address': 'г. Москва, ул. Пушкина', 'dogovor_number': '10/2025',
            'dogovor_date': '01.01.2025', 'obyazatelstvo': 'поставить товар',
            'narushenie': 'товар не поставлен', 'trebovanie': 'вернуть предоплату',
            'pretenziya_summa': '200000', 'summa_words': 'двести тысяч',
            'srok_otveta': 10, 'lawyer_name': 'Юристов Ю.Ю.',
        }
    ),
    (
        'doverennost.docx',
        {
            'number': '004', 'data': '19.06.2025', 'gorod': 'Москва',
            'org_name': 'ООО Организация', 'org_inn': '7707083893',
            'org_address': 'г. Москва, ул. Ленина', 'director_name': 'Иванов И.И.',
            'poverenny_name': 'Петров П.П.', 'poverenny_pasport': '4500 123456',
            'poverenny_address': 'г. Москва, ул. Мира', 'polnomochiya': 'подписывать договоры',
            'srok_do': '31.12.2025',
        }
    ),
    (
        'iskovoe.docx',
        {
            'data': '19.06.2025', 'sud_name': 'Арбитражный суд г. Москвы',
            'istec_name': 'ООО Истец', 'istec_address': 'г. Москва',
            'istec_inn': '7707083893', 'otvetchik_name': 'ООО Ответчик',
            'otvetchik_address': 'г. Санкт-Петербург', 'otvetchik_inn': '7736207543',
            'dogovor_number': '5/2025', 'dogovor_date': '01.03.2025',
            'narushenie': 'не оплатил товар', 'pretenziya_date': '01.05.2025',
            'iskovye_trebovaniya': 'взыскать задолженность', 'summa_iska': '300000',
            'summa_words': 'триста тысяч', 'lawyer_name': 'Адвокатов А.А.',
        }
    ),
]


@pytest.mark.parametrize('filename,context', ШАБЛОНЫ_И_КОНТЕКСТЫ,
                         ids=[x[0] for x in ШАБЛОНЫ_И_КОНТЕКСТЫ])
def test_шаблон_рендерится_без_незакрытых_тегов(tmp_path, filename, context):
    template = settings.WORD_TEMPLATES_DIR / filename
    out = tmp_path / f'result_{filename}'
    render_docx(template, context, out)

    assert out.exists(), f'{filename}: файл не создан'
    assert out.stat().st_size > 0

    with zipfile.ZipFile(out) as z:
        xml = z.read('word/document.xml').decode('utf-8')

    assert '{{' not in xml, f'{filename}: остались незакрытые теги {{}}'
    assert '}}' not in xml, f'{filename}: остались незакрытые теги }}}}'
