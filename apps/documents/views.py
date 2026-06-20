"""Вьюхи документов: выбор шаблона, динамическая форма, генерация, журнал, скачивание."""
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.templates_engine.models import ШаблонДокумента
from apps.templates_engine.services import convert_to_pdf, render_docx, libreoffice_available
from apps.accounts.utils import требует_группу, ВСЕ_РОЛИ, РОЛЬ_ЮРИСТ, РОЛЬ_ПОМОЩНИК, РОЛЬ_АДМИН
from .forms import ДинамическаяФорма
from .models import СгенерированныйДокумент

_LIBREOFFICE_AVAILABLE = libreoffice_available()


@login_required
def index(request):
    последние = СгенерированныйДокумент.objects.filter(
        автор=request.user
    ).select_related('шаблон', 'контрагент')[:5]
    return render(request, 'documents/index.html', {'последние': последние})


@требует_группу(*ВСЕ_РОЛИ)
def select_template(request):
    шаблоны = ШаблонДокумента.objects.filter(активен=True).annotate(
        кол_во_полей=Count('переменные')
    )
    return render(request, 'documents/select_template.html', {'шаблоны': шаблоны})


@требует_группу(РОЛЬ_ЮРИСТ, РОЛЬ_ПОМОЩНИК, РОЛЬ_АДМИН)
def create(request, template_id):
    шаблон = get_object_or_404(ШаблонДокумента, pk=template_id, активен=True)

    if request.method == 'POST':
        форма = ДинамическаяФорма(шаблон, request.POST)
        if форма.is_valid():
            doc = _генерировать(request, шаблон, форма)
            return redirect('documents:detail', pk=doc.pk)
    else:
        форма = ДинамическаяФорма(шаблон)

    return render(request, 'documents/create.html', {
        'шаблон': шаблон,
        'форма': форма,
        'libreoffice_available': _LIBREOFFICE_AVAILABLE,
    })


@требует_группу(*ВСЕ_РОЛИ)
def journal(request):
    docs = СгенерированныйДокумент.objects.filter(
        автор=request.user
    ).select_related('шаблон', 'контрагент')

    q = request.GET.get('q', '').strip()
    тип = request.GET.get('тип', '').strip()
    дата_с = request.GET.get('дата_с', '').strip()
    дата_по = request.GET.get('дата_по', '').strip()
    статус = request.GET.get('статус', '').strip()

    if q:
        docs = docs.filter(
            Q(шаблон__название__icontains=q) | Q(контрагент__наименование__icontains=q)
        )
    if тип:
        docs = docs.filter(шаблон__тип=тип)
    if статус:
        docs = docs.filter(статус=статус)
    if дата_с:
        docs = docs.filter(создан__date__gte=дата_с)
    if дата_по:
        docs = docs.filter(создан__date__lte=дата_по)

    docs = docs.order_by('-создан')

    ctx = {
        'типы': ШаблонДокумента.ТИП_ВЫБОР,
        'статусы': СгенерированныйДокумент.СТАТУС_ВЫБОР,
        'q': q,
        'тип': тип,
        'статус': статус,
        'дата_с': дата_с,
        'дата_по': дата_по,
    }

    if request.htmx:
        # HTMX-запрос: возвращаем только строки таблицы (без пагинации)
        ctx['docs'] = docs[:100]
        ctx['total'] = docs.count()
        return render(request, 'documents/_journal_rows.html', ctx)

    paginator = Paginator(docs, 10)
    ctx['docs'] = paginator.get_page(request.GET.get('page', 1))
    ctx['total'] = paginator.count
    return render(request, 'documents/journal.html', ctx)


@требует_группу(*ВСЕ_РОЛИ)
def detail(request, pk):
    doc = get_object_or_404(СгенерированныйДокумент, pk=pk, автор=request.user)
    return render(request, 'documents/detail.html', {'doc': doc})


@требует_группу(*ВСЕ_РОЛИ)
def download(request, pk, fmt):
    doc = get_object_or_404(СгенерированныйДокумент, pk=pk, автор=request.user)

    if fmt == 'docx' and doc.файл_docx:
        path = Path(doc.файл_docx.path)
        mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif fmt == 'pdf' and doc.файл_pdf:
        path = Path(doc.файл_pdf.path)
        mime = 'application/pdf'
    else:
        raise Http404

    # Защита от path traversal: итоговый путь обязан лежать внутри MEDIA_ROOT.
    media_root = Path(settings.MEDIA_ROOT).resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(media_root):
        raise Http404

    if not resolved.exists():
        raise Http404

    return FileResponse(
        open(resolved, 'rb'), content_type=mime, as_attachment=True, filename=resolved.name
    )


def _генерировать(request, шаблон, форма) -> СгенерированныйДокумент:
    контрагент = форма.cleaned_data['контрагент']
    контекст = форма.получить_контекст()
    uid = uuid.uuid4().hex[:8]

    # transaction.atomic: запись о документе и её итоговый статус коммитятся
    # одной транзакцией. При жёстком завершении процесса (OOM/SIGKILL) посреди
    # генерации в БД не останется «висячего» черновика без файлов.
    with transaction.atomic():
        doc = СгенерированныйДокумент.objects.create(
            шаблон=шаблон,
            автор=request.user,
            контрагент=контрагент,
            значения=контекст,
            статус='черновик',
        )

        try:
            docx_dir = Path(settings.MEDIA_ROOT) / 'documents' / 'docx'
            pdf_dir = Path(settings.MEDIA_ROOT) / 'documents' / 'pdf'

            docx_name = f'{шаблон.тип}_{uid}.docx'
            docx_path = docx_dir / docx_name

            render_docx(шаблон.файл.path, контекст, docx_path)
            doc.файл_docx.name = f'documents/docx/{docx_name}'

            if _LIBREOFFICE_AVAILABLE:
                pdf_path = convert_to_pdf(docx_path, pdf_dir)
                doc.файл_pdf.name = f'documents/pdf/{pdf_path.name}'

            doc.статус = 'готов'

        except Exception as e:
            doc.статус = 'ошибка'
            doc.ошибка = str(e)

        doc.save()

    return doc
