from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
   path('i18n/', include('django.conf.urls.i18n')),  # подключаем встроенные эндопинты для работы с локализацией
   path('admin/', admin.site.urls),
   path('pages/', include('django.contrib.flatpages.urls')),
   path('', include('simpleapp.urls')),
   path('account/', include('protect.urls')),
   path('sign/', include('sign.urls')),
   path('appointments/', include(('appointment.urls', 'appointments'), namespace='appointments')),
   path('ckeditor/', include('ckeditor_uploader.urls')),  # Подключаем CKEditor

]

# В режиме разработки раздаем медиафайлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)