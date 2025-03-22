from django.contrib import admin
from django.urls import path
from authuser.views import index_page, profile, logout, settings_page, friends, messages
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name='index_page'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('friends/', friends, name='friends'),
    path('messages/', messages, name='messages'),
    path('settings/', settings_page, name='settings'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)