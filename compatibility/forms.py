from django import forms
from .models import ComparisonSettings, SelectedCriterion, PairsCriteria, Review
from authuser.models import City, Zodiac, Religion, Alcohol, Smoking, Children, Education, Language, Interest

class SelectedCriterionForm(forms.ModelForm):
    class Meta:
        model = SelectedCriterion
        fields = ['criteria']
        widgets = {
            'criteria': forms.CheckboxSelectMultiple,
        }

    def clean_criteria(self):
        criteria = self.cleaned_data.get('criteria')
        if not criteria:
            raise forms.ValidationError("Выберите хотя бы один критерий")
        return criteria


class ComparisonSettingsForm(forms.ModelForm):
    class Meta:
        model = ComparisonSettings
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'profile') and user.profile:
            profile = user.profile
            self.fields['city'].initial = profile.city
            self.fields['zodiac_sign'].initial = profile.zodiac_sign
            self.fields['religion'].initial = profile.religion
            self.fields['alcohol'].initial = profile.alcohol
            self.fields['smoking'].initial = profile.smoking
            self.fields['children'].initial = profile.children
            self.fields['education'].initial = profile.education
            self.fields['age_min'].initial = profile.age
            self.fields['age_max'].initial = profile.age

            interests_qs = profile.interests.all()
            self.fields['interests'].widget = forms.CheckboxSelectMultiple(
                attrs={'class': 'interest-checkbox'}
            )
            self.fields['interests'].queryset = interests_qs
            self.fields['interests'].initial = interests_qs

            self.fields['languages'].widget = forms.CheckboxSelectMultiple(
                attrs={'class': 'languages-checkbox'}
            )
            self.fields['languages'].queryset = profile.language.all()
            self.fields['languages'].initial = profile.language.all()

        selected_criterion = SelectedCriterion.objects.filter(user=user).first()
        selected_codes = selected_criterion.criteria.values_list('code', flat=True) if selected_criterion else []

        field_map = {
            'city': ['city'],
            'zodiac': ['zodiac_sign'],
            'religion': ['religion'],
            'alcohol': ['alcohol'],
            'smoking': ['smoking'],
            'children': ['children'],
            'education': ['education'],
            'languages': ['languages'],
            'age': ['age_min', 'age_max'],
            'interests' : ['interests']
        }

        for code, fields in field_map.items():
            if code not in selected_codes:
                for field in fields:
                    if field in self.fields:
                        del self.fields[field]

class PairsCriteriaForm(forms.ModelForm):
    class Meta:
        model = PairsCriteria
        fields = ['score']
        widgets = {'score': forms.RadioSelect(attrs={'class': 'score-radio'})}

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Опишите ваши впечатления...'
            }),
        }
        labels = {
            'rating': 'Оценка',
            'text': 'Текст отзыва'
        }