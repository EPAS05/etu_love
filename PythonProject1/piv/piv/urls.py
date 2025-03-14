from django.contrib import admin
from django.urls import path
from authuser.views import index_page, profile, logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name='index_page'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    #path('friends/', friends_view, name='friends'),
    #path('messages/', messages_view, name='messages'),
    #path('settings/', settings_view, name='settings'),
]