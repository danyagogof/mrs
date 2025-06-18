from django.contrib import admin
from .models import Album, Rating, CustomUser

admin.site.register(Album)
admin.site.register(Rating)
admin.site.register(CustomUser)