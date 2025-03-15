from django.db import models
from django.contrib.auth.hashers import make_password, check_password

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
    birth_date = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    interests = models.ManyToManyField('Interest', blank = True)
    music = models.ManyToManyField('Music', blank = True)

class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Music(models.Model):
    name = models.CharField(max_length=50, unique=True)
