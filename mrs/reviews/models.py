from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.conf import settings

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Ця пошта вже використовується")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("username", email)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("username", email)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = models.CharField(
        "нікнейм",
        max_length=20,
        unique=True,
        help_text="Обов'язкове поле. 20 символів або менше. Лише літери, цифри та @/./+/-/_.",
        error_messages={
            'unique': "Користувач з таким нікнеймом вже існує.",
        },
    )
    email = models.EmailField("електронна пошта", unique=True)
    friends = models.ManyToManyField('self', blank=True)
    avatar = models.ImageField("Аватарка", upload_to="avatars/", blank=True, null=True)
    bio = models.TextField("Опис про себе", blank=True, null=True)
    contacts = models.CharField("Контактна інформація", max_length=255, blank=True, null=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

class Album(models.Model):
    spotify_id = models.CharField("Spotify ID", max_length=100, unique=True, db_index=True)
    title = models.CharField("Назва", max_length=200)
    artist = models.CharField("Виконавець", max_length=200)
    release_year = models.IntegerField("Рік випуску") 
    cover_image_url = models.URLField("URL обкладинки", blank=True, null=True)

    def __str__(self):
        return f'"{self.title}" - {self.artist} ({self.release_year})'

class Rating(models.Model):
    score = models.PositiveSmallIntegerField("Оцінка")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'album')

    def __str__(self):
        return f'Оцінка для {self.album.title} від {self.user.email}'