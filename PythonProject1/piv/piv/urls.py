from django.contrib import admin
from django.urls import path
from authuser.views import index_page, profile, logout, settings_page, friends, messages, edit_extra_profile, edit_main_profile
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
    path('profile/edit', edit_extra_profile, name='editExtra'),
    path('settings/profile', edit_main_profile, name='editMain'),
    #path('search/', poisk, name='poisk')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)