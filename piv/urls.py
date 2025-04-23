from django.contrib import admin
from django.urls import path
from authuser.views import index_page, profile, logout, settings_page, messages_page, delete_photo
from compatibility.views import search_settings, compare_criteria, user_profile, friends, send_friend_request, cancel_friend_request, accept_friend_request, decline_friend_request, remove_friend
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name='index_page'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('messages/', messages_page, name='messages_page'),
    path('settings/', settings_page, name='settings_page'),
    path('search/', search_settings, name='search_settings'),
    path('compare/', compare_criteria, name='compare_criteria'),
    path('profile/<int:user_id>/',user_profile, name='user_profile'),
    path('friends/', friends, name='friends'),
    path('friends/send/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('friends/cancel/<int:friendship_id>/', cancel_friend_request, name='cancel_friend_request'),
    path('friends/accept/<int:friendship_id>/', accept_friend_request, name='accept_friend_request'),
    path('friends/decline/<int:friendship_id>/', decline_friend_request, name='decline_friend_request'),
    path('friends/remove/<int:friend_id>/', remove_friend, name='remove_friend'),
    path('profile/delete_photo/<str:photo_uuid>/', delete_photo, name='delete_photo')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)