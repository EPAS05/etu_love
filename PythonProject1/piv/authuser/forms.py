from django import forms
from .models import *
from django.core.exceptions import ValidationError

class RegistrationForm(forms.Form):
    full_name = forms.CharField(label='Полное имя')
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        if data.get('password') != data.get('confirm_password'):
            raise forms.ValidationError("Пароли не совпадают")

        if User.objects.filter(email=data.get('email')).exists():
            raise forms.ValidationError("Email уже существует")

        return data

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Текущий пароль'})
    )
    new_password = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'})
    )
    confirm_password = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise ValidationError("Пароли не совпадают")

        return cleaned_data


class EditProfileForm(forms.ModelForm):
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    music = forms.ModelMultipleChoiceField(
        queryset=Music.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    language = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            'avatar', 'photo1', 'photo2', 'photo3', 'photo4', 'photo5',
            'gender', 'job', 'birth_date', 'bio', 'height', 'city',
            'zodiac_sign', 'smoking', 'alcohol', 'religion', 'education',
            'children', 'interests', 'music', 'language', 'theme_id', 'emodji_id'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'maxlength': 200}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'min': 100, 'max': 250}),
            'job': forms.TextInput(attrs={'class': 'form-control'}),
            'theme_id': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'emodji_id': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'zodiac_sign': forms.Select(attrs={'class': 'form-select'}),
            'smoking': forms.Select(attrs={'class': 'form-select'}),
            'alcohol': forms.Select(attrs={'class': 'form-select'}),
            'religion': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'children': forms.Select(attrs={'class': 'form-select'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'photo1': forms.FileInput(attrs={'class': 'form-control'}),
            'photo2': forms.FileInput(attrs={'class': 'form-control'}),
            'photo3': forms.FileInput(attrs={'class': 'form-control'}),
            'photo4': forms.FileInput(attrs={'class': 'form-control'}),
            'photo5': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['gender', 'city', 'zodiac_sign', 'smoking', 'alcohol',
                      'religion', 'education', 'children']:
            self.fields[field].empty_label = "Не указано"

    def clean_job(self):
        job = self.cleaned_data.get('job')
        if job and len(job) > 20:
            raise forms.ValidationError("Максимальная длина - 20 символов")
        return job

    def _validate_image(self, image):
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Максимальный размер файла - 5 МБ")
            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                raise forms.ValidationError("Допустимые форматы: PNG, JPG, JPEG, WEBP")
        return image

    def clean_avatar(self):
        return self._validate_image(self.cleaned_data.get('avatar'))

    def clean_photo1(self):
        return self._validate_image(self.cleaned_data.get('photo1'))

    def clean_photo2(self):
        return self._validate_image(self.cleaned_data.get('photo2'))

    def clean_photo3(self):
        return self._validate_image(self.cleaned_data.get('photo3'))

    def clean_photo4(self):
        return self._validate_image(self.cleaned_data.get('photo4'))

    def clean_photo5(self):
        return self._validate_image(self.cleaned_data.get('photo5'))