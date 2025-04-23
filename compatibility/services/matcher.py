from compatibility.models import CriterionWeight, ComparisonSettings, SelectedCriterion

class MatcherCalc:
    @staticmethod
    def find_compability(user, other_profile):
        selected = SelectedCriterion.objects.get(user=user)
        criteria = selected.criteria.all()
        weights = CriterionWeight.objects.filter(user=user, criterion__in=criteria)
        weight_dict = {w.criterion.code: w.weight for w in weights}

        total_score = 0
        settings = user.comparison_settings

        manyToMany_fields = {
            'languages': {
                'model_field': 'language',
                'settings_field': settings.languages
            },
            'interests': {
                'model_field': 'interests',
                'settings_field': settings.interests
            }
        }

        for code, config in manyToMany_fields.items():
            if code in weight_dict and config['settings_field'].exists():
                selected_count = config['settings_field'].count()
                common_count = getattr(other_profile, config['model_field']).filter(
                    id__in=config['settings_field'].values_list('id', flat=True)
                ).count()

                if selected_count > 0:
                    ratio = common_count / selected_count
                    total_score += weight_dict[code] * ratio

        age_condition = False
        if settings.age_min is not None and settings.age_max is not None:
            age_condition = settings.age_min <= other_profile.age <= settings.age_max

        other_criteria = {
            'city': (other_profile.city == settings.city, 'city'),
            'zodiac': (other_profile.zodiac_sign == settings.zodiac_sign, 'zodiac'),
            'religion': (other_profile.religion == settings.religion, 'religion'),
            'alcohol': (other_profile.alcohol == settings.alcohol, 'alcohol'),
            'smoking': (other_profile.smoking == settings.smoking, 'smoking'),
            'children': (other_profile.children == settings.children, 'children'),
            'education': (other_profile.education == settings.education, 'education'),
            'age':     (age_condition, 'age'),
        }

        for criterion in criteria:
            code = criterion.code
            if code in other_criteria:
                condition, weight_key = other_criteria[code]
                if condition and code in weight_dict:
                    total_score += weight_dict[code]

        return min(round(total_score * 100, 1), 100)
