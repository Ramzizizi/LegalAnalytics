from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler403 = 'django.views.defaults.permission_denied'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('search/', include('apps.search.urls')),
    path('builder/', include('apps.builder.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('knowledge/', include('apps.knowledge.urls')),
    path('', include('apps.catalog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
