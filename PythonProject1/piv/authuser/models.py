from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        return self.is_active

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    photo1 = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name="Фото 1")
    photo2 = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name="Фото 2")
    photo3 = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name="Фото 3")
    photo4 = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name="Фото 4")
    photo5 = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name="Фото 5")
    gender = models.ForeignKey('Gender', on_delete=models.SET_NULL, blank=True, null=True)
    job = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.CharField(max_length=200, blank=True, null=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL, blank=True, null=True)
    interests = models.ManyToManyField('Interest', blank=True)
    music = models.ManyToManyField('Music', blank=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    zodiac_sign = models.ForeignKey('Zodiac', on_delete=models.SET_NULL, blank=True, null=True)
    smoking = models.ForeignKey('Smoking', on_delete=models.SET_NULL, blank=True, null=True)
    alcohol = models.ForeignKey('Alcohol', on_delete=models.SET_NULL, blank=True, null=True)
    religion = models.ForeignKey('Religion', on_delete=models.SET_NULL, blank=True, null=True)
    education = models.ForeignKey('Education', on_delete=models.SET_NULL, blank=True, null=True)
    children = models.ForeignKey('Children', on_delete=models.SET_NULL, blank=True, null=True)
    language = models.ManyToManyField('Language', blank=True, null=True)
    theme_id = models.PositiveIntegerField(default=1)
    emodji_id = models.PositiveIntegerField(default=1)

class Interest(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Music(models.Model):
    name = models.CharField(max_length=20, unique=True)

class City(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Language(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Children(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Smoking(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Alcohol(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Religion(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Zodiac(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Education(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Gender(models.Model):
    name = models.CharField(max_length=20, unique=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()