from django import forms
from .models import User, Profile, Interest, City, Language, Children, Smoking, Alcohol, Religion, Zodiac, Education, Gender
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

class EditMainProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100,
        label="Полное имя",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'})
    )

    class Meta:
        fields = ['avatar', 'gender', 'birth_date', 'city', 'bio']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'maxlength': 200}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'photo1': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def _validate_image(self, image):
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Максимальный размер файла - 5 МБ")
            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                raise forms.ValidationError("Допустимые форматы: PNG, JPG, JPEG, WEBP")
        return image

    def clean_avatar(self):
        return self._validate_image(self.cleaned_data.get('avatar'))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['full_name'].initial = user.full_name
            self.fields['city'].empty_label = "Не указано"
            self.fields['gender'].empty_label = "Не указано"

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if len(full_name) < 3:
            raise forms.ValidationError("Полное имя должно содержать не менее 3 символов")
        return full_name

    def save(self, user, commit=True):
        user.full_name = self.cleaned_data.get('full_name')
        user.save()
        return super().save(commit=commit)

class EditExtraProfileForm(forms.ModelForm):
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
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
            'photo1', 'photo2', 'photo3', 'photo4', 'photo5',
            'job', 'height',
            'zodiac_sign', 'smoking', 'alcohol', 'religion', 'education',
            'children', 'interests', 'language',
        ]
        widgets = {
            'height': forms.NumberInput(attrs={'class': 'form-control', 'min': 100, 'max': 250}),
            'job': forms.TextInput(attrs={'class': 'form-control'}),
            'zodiac_sign': forms.Select(attrs={'class': 'form-select'}),
            'smoking': forms.Select(attrs={'class': 'form-select'}),
            'alcohol': forms.Select(attrs={'class': 'form-select'}),
            'religion': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'children': forms.Select(attrs={'class': 'form-select'}),
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

    def save(self, user, commit=True):
        profile = Profile.objects.get(user=user)
        profile.interests.set(self.cleaned_data.get('interests'))
        profile.language.set(self.cleaned_data.get('language'))
        return super().save(commit=commit)