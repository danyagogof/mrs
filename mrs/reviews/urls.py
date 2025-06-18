from django.urls import path
from .views import (
    SignUpView, 
    HomePageView, 
    AlbumSearchView, 
    AlbumDetailView,
    ProfileView,
    ProfileUpdateView,
    UserSearchView,
    AddFriendView,
    RemoveFriendView,
    FriendProfileView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('search/', AlbumSearchView.as_view(), name='album_search'),
    path('album/<str:spotify_id>/', AlbumDetailView.as_view(), name='album_detail'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_update'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('users/', UserSearchView.as_view(), name='user_search'),
    path('users/add/<int:user_id>/', AddFriendView.as_view(), name='add_friend'),
    path('users/remove/<int:user_id>/', RemoveFriendView.as_view(), name='remove_friend'),
    path('profile/<int:user_id>/', FriendProfileView.as_view(), name='friend_profile'),
]