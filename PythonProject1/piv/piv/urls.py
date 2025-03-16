from django.contrib import admin
from django.urls import path
from authuser.views import index_page, profile, logout, settings, friends, messages

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name='index_page'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('friends/', friends, name='friends'),
    path('messages/', messages, name='messages'),
    path('settings/', settings, name='settings'),
]