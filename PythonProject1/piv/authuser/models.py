from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from datetime import date

class User(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        return self.is_active

    def has_perm(self, perm, obj=None):
        return self.is_superuser  # Только суперпользователь имеет все права

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_username(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default_avatar.jpg')
    gender = models.ForeignKey('Gender', on_delete=models.SET_NULL, blank=True, null=True)
    job = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.CharField(max_length=200, blank=True, null=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL, blank=True, null=True)
    interests = models.ManyToManyField('Interest', blank=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    zodiac_sign = models.ForeignKey('Zodiac', on_delete=models.SET_NULL, blank=True, null=True)
    smoking = models.ForeignKey('Smoking', on_delete=models.SET_NULL, blank=True, null=True)
    alcohol = models.ForeignKey('Alcohol', on_delete=models.SET_NULL, blank=True, null=True)
    religion = models.ForeignKey('Religion', on_delete=models.SET_NULL, blank=True, null=True)
    education = models.ForeignKey('Education', on_delete=models.SET_NULL, blank=True, null=True)
    children = models.ForeignKey('Children', on_delete=models.SET_NULL, blank=True, null=True)
    language = models.ManyToManyField('Language', blank=True, null=True)
    emodji_id = models.PositiveIntegerField(default=1)

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        born = self.birth_date
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def get_zodiac_sign(birth_date):
    if (birth_date.month == 12 and birth_date.day >= 22) or (birth_date.month == 1 and birth_date.day <= 19):
        return "Козерог"
    elif (birth_date.month == 1 and birth_date.day >= 20) or (birth_date.month == 2 and birth_date.day <= 18):
        return "Водолей"
    elif (birth_date.month == 2 and birth_date.day >= 19) or (birth_date.month == 3 and birth_date.day <= 20):
        return "Рыбы"
    elif (birth_date.month == 3 and birth_date.day >= 21) or (birth_date.month == 4 and birth_date.day <= 19):
        return "Овен"
    elif (birth_date.month == 4 and birth_date.day >= 20) or (birth_date.month == 5 and birth_date.day <= 20):
        return "Телец"
    elif (birth_date.month == 5 and birth_date.day >= 21) or (birth_date.month == 6 and birth_date.day <= 20):
        return "Близнецы"
    elif (birth_date.month == 6 and birth_date.day >= 21) or (birth_date.month == 7 and birth_date.day <= 22):
        return "Рак"
    elif (birth_date.month == 7 and birth_date.day >= 23) or (birth_date.month == 8 and birth_date.day <= 22):
        return "Лев"
    elif (birth_date.month == 8 and birth_date.day >= 23) or (birth_date.month == 9 and birth_date.day <= 22):
        return "Дева"
    elif (birth_date.month == 9 and birth_date.day >= 23) or (birth_date.month == 10 and birth_date.day <= 22):
        return "Весы"
    elif (birth_date.month == 10 and birth_date.day >= 23) or (birth_date.month == 11 and birth_date.day <= 21):
        return "Скорпион"
    elif (birth_date.month == 11 and birth_date.day >= 22) or (birth_date.month == 12 and birth_date.day <= 21):
        return "Стрелец"
    else:
        return None

def profile_photo_upload_to(instance, filename):
    return os.path.join("profile_photos", str(instance.profile.user.id), filename)

class ProfilePhoto(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to=profile_photo_upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.id} for {self.profile.user.get_username()}"

class Interest(models.Model):
    name = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to='interests/', blank=True, null=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Children(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Smoking(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Alcohol(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Religion(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Zodiac(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Education(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Gender(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()