from django.contrib import admin
from .models import User, Profile, Interest, City, Language, Children, Smoking, Alcohol, Religion, Zodiac, Education, Gender

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'is_active')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'city')

# Зарегистрировать остальные модели
admin.site.register(Interest)
admin.site.register(City)
admin.site.register(Language)
admin.site.register(Children)
admin.site.register(Smoking)
admin.site.register(Alcohol)
admin.site.register(Religion)
admin.site.register(Zodiac)
admin.site.register(Education)
admin.site.register(Gender)
