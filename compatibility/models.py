from django.db import models
from authuser.models import User, Profile, Zodiac, Religion, City, Children, Alcohol, Language, Smoking, Interest, Education

class Criterion(models.Model):
    name = models.CharField(max_length=30)
    code = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class SelectedCriterion(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    criteria = models.ManyToManyField(Criterion)
    created_at = models.DateTimeField(auto_now_add=True)


class ComparisonSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='comparison_settings')

    age_min = models.PositiveIntegerField("Мин. возраст", null=True, blank=True)
    age_max = models.PositiveIntegerField("Макс. возраст", null=True, blank=True)

    city = models.ForeignKey(City, on_delete=models.SET_NULL, verbose_name="Город", null=True, blank=True)
    zodiac_sign = models.ForeignKey(Zodiac, on_delete=models.SET_NULL, verbose_name="Знак зодиака", null=True, blank=True)
    religion = models.ForeignKey(Religion, on_delete=models.SET_NULL, verbose_name="Религия", null=True, blank=True)
    alcohol = models.ForeignKey(Alcohol, on_delete=models.SET_NULL, verbose_name="Алкоголь", null=True, blank=True)
    smoking = models.ForeignKey(Smoking, on_delete=models.SET_NULL, verbose_name="Курение", null=True, blank=True)
    children = models.ForeignKey(Children, on_delete=models.SET_NULL, verbose_name="Дети", null=True, blank=True)
    education = models.ForeignKey(Education, on_delete=models.SET_NULL, verbose_name="Образование", null=True, blank=True)
    languages = models.ManyToManyField(Language, verbose_name="Языки", blank=True)
    interests = models.ManyToManyField(Interest, verbose_name="Интересы", blank=True)

    class Meta:
        verbose_name = "Настройки поиска"
        verbose_name_plural = "Настройки поиска"

    def __str__(self):
        return f"Для {self.user.email}"

class PairsCriteria(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    criterion_a = models.ForeignKey(Criterion, related_name='comparisons_a', on_delete=models.CASCADE)
    criterion_b = models.ForeignKey(Criterion, related_name='comparisons_b', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(
        choices=[
            (1, 'Значительно важнее'),
            (2, 'Немного важнее'),
            (3, 'Одинаково'),
            (4, 'Немного менее важно'),
            (5, 'Значительно менее важно')
        ],
        default=3
    )

    class Meta:
        unique_together = ['user', 'criterion_a', 'criterion_b']
        ordering = ['criterion_a', 'criterion_b']

    def __str__(self):
        return f"{self.criterion_a} vs {self.criterion_b} ({self.score})"

class CriterionWeight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)
    weight = models.FloatField()
    consistency_ratio = models.FloatField(default=0.0)

    class Meta:
        unique_together = ['user', 'criterion']

class Friendship(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('accepted', 'Принято'),
        ('declined', 'Отклонено'),
    )

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recieved')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    text = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('author', 'receiver')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author} для {self.receiver} ({self.rating})"