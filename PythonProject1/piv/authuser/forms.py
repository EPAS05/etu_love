from django import forms
from .models import User, Profile, Interest, City, Language, Children, Smoking, Alcohol, Religion, Zodiac, Education, Gender, ProfilePhoto, get_zodiac_sign
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return []

        cleaned_data = []
        for d in data:
            cleaned = super(MultipleFileField, self).clean(d, initial)
            cleaned_data.append(cleaned)
        return cleaned_data

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
        model = Profile
        fields = ['avatar', 'gender', 'birth_date', 'city', 'bio']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'maxlength': 200}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'})
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
        profile = super().save(commit=False)

        if not self.cleaned_data.get('avatar'):
            profile.avatar = 'avatars/default_avatar.jpg'

        if commit:
            profile.save()
        return profile

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

    photos = MultipleFileField(
        required=False,
        label="Добавить фотографии",
        help_text="Можно выбрать несколько файлов",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )

    zodiac_sign = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select()
    )

    class Meta:
        model = Profile
        fields = [
            'job', 'height', 'zodiac_sign',
            'smoking', 'alcohol', 'religion',
            'education', 'children', 'interests',
            'language'
        ]
        widgets = {
            'height': forms.NumberInput(attrs={'min': 100, 'max': 250}),
            'job': forms.TextInput(),
            'smoking': forms.Select(),
            'alcohol': forms.Select(),
            'religion': forms.Select(),
            'education': forms.Select(),
            'children': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in ['smoking', 'alcohol', 'religion', 'education', 'children']:
            self.fields[field].empty_label = "Не указано"

        new_choices = [("", "Не указано")]
        computed = None
        if self.instance and self.instance.birth_date:
            computed = get_zodiac_sign(self.instance.birth_date)
        if computed:
            new_choices.append(("auto", f"Показывать мой знак ({computed})"))
        self.fields["zodiac_sign"].choices = new_choices

        if self.instance and self.instance.zodiac_sign:
            self.initial["zodiac_sign"] = "auto"
        else:
            self.initial["zodiac_sign"] = ""

    def clean_job(self):
        job = self.cleaned_data.get('job')
        if job and len(job) > 20:
            raise forms.ValidationError("Максимальная длина - 20 символов")
        return job

    def clean_photos(self):
        photos = self.files.getlist('photos')
        max_size = 5 * 1024 * 1024  # 5MB

        for photo in photos:
            if photo.size > max_size:
                raise forms.ValidationError(
                    f"Файл {photo.name} слишком большой (максимум 5 МБ)"
                )
        return photos

    def clean_zodiac_sign(self):
        value = self.cleaned_data.get("zodiac_sign")
        if value == "auto":
            if self.instance and self.instance.birth_date:
                zodiac_name = get_zodiac_sign(self.instance.birth_date)
                if zodiac_name:
                    try:
                        zodiac_obj = Zodiac.objects.get(name=zodiac_name)
                        return zodiac_obj
                    except Zodiac.DoesNotExist:
                        raise forms.ValidationError(f"Знак зодиака '{zodiac_name}' не найден в базе")
                else:
                    raise forms.ValidationError("Невозможно вычислить знак зодиака")
            else:
                raise forms.ValidationError("Дата рождения не указана")
        elif value == "":
            return None
        else:
            return value

    def save(self, commit=True):
        instance = super().save(commit=commit)
        for photo in self.cleaned_data.get('photos', []):
            ProfilePhoto.objects.create(profile=instance, image=photo)
        return instance