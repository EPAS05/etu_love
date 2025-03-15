from django import forms
from .models import User, Interest, Profile, Music

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

class EditProfileForm(forms.Form):
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    music = forms.ModelMultipleChoiceField(
        queryset=Music.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = Profile
        fields = ['avatar', 'birth_date', 'city', 'interests', 'music']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'})
        }