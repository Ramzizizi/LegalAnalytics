from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('catalog/', include('apps.catalog.urls')),
    path('templates/', include('apps.templates_engine.urls')),
    path('', include('apps.documents.urls')),
]

# Прямая раздача media — ТОЛЬКО для разработки. В продакшне сгенерированные
# документы отдаются через вьюху documents.download с проверкой автора;
# открытый маршрут на MEDIA_URL позволил бы скачать чужой документ по имени файла.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
