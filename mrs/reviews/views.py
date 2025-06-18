from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View, DetailView
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .forms import CustomUserCreationForm, UserUpdateForm
from .models import Album, Rating, CustomUser
from django.db.models import Avg, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.urls import reverse

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class HomePageView(ListView):
    model = Album
    template_name = 'home.html'
    context_object_name = 'albums'
    def get_queryset(self):
        return Album.objects.annotate(avg_score=Avg('ratings__score')).order_by('-avg_score', 'title')

class AlbumSearchView(View):
    def get(self, request):
        query = request.GET.get('q')
        artist = request.GET.get('artist')
        results = []
        auth_manager = SpotifyClientCredentials(
            client_id=settings.SPOTIPY_CLIENT_ID,
            client_secret=settings.SPOTIPY_CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        if artist and not query:
            artist_results = sp.search(q=f'artist:{artist}', type='artist', limit=1)
            items = artist_results['artists']['items']
            if items:
                artist_id = items[0]['id']
                albums_response = sp.artist_albums(artist_id, album_type='album', limit=50)
                all_albums = albums_response['items']
                while albums_response.get('next'):
                    albums_response = sp.next(albums_response)
                    all_albums.extend(albums_response['items'])
                seen = set()
                results = []
                for album in all_albums:
                    artist_ids = [a['id'] for a in album['artists']]
                    if artist_id in artist_ids and album.get('album_type') == 'album':
                        key = (album['name'].lower(), album['release_date'])
                        if key not in seen:
                            seen.add(key)
                            results.append(album)
        elif query and artist:
            search_query = f'album:{query} artist:{artist}'
            response = sp.search(q=search_query, type='album', limit=10)
            results = response['albums']['items']
        elif query:
            response = sp.search(q=query, type='album', limit=10)
            results = response['albums']['items']
        return render(request, 'album_search.html', {'results': results, 'query': query, 'artist': artist})

class AlbumDetailView(View):
    def get(self, request, spotify_id):
        album = Album.objects.filter(spotify_id=spotify_id).first()
        tracklist = []
        if not album:
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=settings.SPOTIPY_CLIENT_ID,
                    client_secret=settings.SPOTIPY_CLIENT_SECRET
                )
                sp = spotipy.Spotify(auth_manager=auth_manager)
                album_data = sp.album(spotify_id)
                album = Album.objects.create(
                    spotify_id=album_data['id'],
                    title=album_data['name'],
                    artist=album_data['artists'][0]['name'],
                    release_year=int(album_data['release_date'][:4]),
                    cover_image_url=album_data['images'][0]['url'] if album_data['images'] else ''
                )
                tracks = album_data['tracks']['items']
                for track in tracks:
                    tracklist.append({
                        'name': track['name'],
                        'explicit': track['explicit'],
                        'track_number': track['track_number'],
                        'preview_url': track['preview_url'],
                    })
            except Exception:
                return redirect('home')
        else:
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=settings.SPOTIPY_CLIENT_ID,
                    client_secret=settings.SPOTIPY_CLIENT_SECRET
                )
                sp = spotipy.Spotify(auth_manager=auth_manager)
                album_data = sp.album(spotify_id)
                tracks = album_data['tracks']['items']
                for track in tracks:
                    tracklist.append({
                        'name': track['name'],
                        'explicit': track['explicit'],
                        'track_number': track['track_number'],
                        'preview_url': track['preview_url'],
                    })
            except Exception:
                pass
        ratings = album.ratings.all()
        return render(request, 'album_detail.html', {
            'album': album,
            'ratings': ratings,
            'tracklist': tracklist,
        })
    def post(self, request, spotify_id):
        album = get_object_or_404(Album, spotify_id=spotify_id)
        score = request.POST.get('score')
        if score:
            Rating.objects.update_or_create(
                user=request.user,
                album=album,
                defaults={'score': int(score)}
            )
        return redirect('album_detail', spotify_id=spotify_id)

class ProfileView(LoginRequiredMixin, ListView):
    model = Rating
    template_name = 'profile.html'
    context_object_name = 'ratings'
    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user).order_by('-created_at')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'profile_update.html'
    success_url = reverse_lazy('profile')
    def get_object(self, queryset=None):
        return self.request.user

class UserSearchView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'user_search.html'
    context_object_name = 'users'
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return CustomUser.objects.filter(
                Q(username__icontains=query) & ~Q(id=self.request.user.id)
            )
        return CustomUser.objects.none()

@method_decorator(require_POST, name='dispatch')
class AddFriendView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        friend = get_object_or_404(CustomUser, id=user_id)
        request.user.friends.add(friend)
        return redirect(reverse('user_search') + f'?q={friend.username}')

@method_decorator(require_POST, name='dispatch')
class RemoveFriendView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        friend = get_object_or_404(CustomUser, id=user_id)
        request.user.friends.remove(friend)
        return redirect(reverse('user_search') + f'?q={friend.username}')

class FriendProfileView(LoginRequiredMixin, ListView):
    model = Rating
    template_name = 'friend_profile.html'
    context_object_name = 'ratings'
    def dispatch(self, request, *args, **kwargs):
        if request.user.id == kwargs.get('user_id'):
            return redirect(reverse('profile'))
        return super().dispatch(request, *args, **kwargs)
    def get_queryset(self):
        self.friend = get_object_or_404(CustomUser, id=self.kwargs['user_id'])
        return Rating.objects.filter(user=self.friend).order_by('-created_at')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['friend'] = self.friend
        context['is_friend'] = self.friend in self.request.user.friends.all()
        return context