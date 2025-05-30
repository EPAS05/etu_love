# Generated by Django 4.2.20 on 2025-04-24 21:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authuser', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Criterion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('code', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SelectedCriterion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('criteria', models.ManyToManyField(to='compatibility.criterion')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ComparisonSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age_min', models.PositiveIntegerField(blank=True, null=True, verbose_name='Мин. возраст')),
                ('age_max', models.PositiveIntegerField(blank=True, null=True, verbose_name='Макс. возраст')),
                ('alcohol', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authuser.alcohol', verbose_name='Алкоголь')),
                ('children', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authuser.children', verbose_name='Дети')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authuser.city', verbose_name='Город')),
                ('education', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authuser.education', verbose_name='Образование')),
                ('interests', models.ManyToManyField(blank=True, to='authuser.interest', verbose_name='Интересы')),
                ('languages', models.ManyToManyField(blank=True, to='authuser.language', verbose_name='Языки')),
                ('religion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authuser.religion', verbose_name='Религия')),
                ('smoking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authuser.smoking', verbose_name='Курение')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='comparison_settings', to=settings.AUTH_USER_MODEL)),
                ('zodiac_sign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authuser.zodiac', verbose_name='Знак зодиака')),
            ],
            options={
                'verbose_name': 'Настройки поиска',
                'verbose_name_plural': 'Настройки поиска',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '1 - Ужасно'), (2, '2 - Плохо'), (3, '3 - Нормально'), (4, '4 - Хорошо'), (5, '5 - Отлично')])),
                ('text', models.TextField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authored', to=settings.AUTH_USER_MODEL)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recieved', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('author', 'receiver')},
            },
        ),
        migrations.CreateModel(
            name='PairsCriteria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField(choices=[(1, 'Значительно важнее'), (2, 'Немного важнее'), (3, 'Одинаково'), (4, 'Немного менее важно'), (5, 'Значительно менее важно')], default=3)),
                ('criterion_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comparisons_a', to='compatibility.criterion')),
                ('criterion_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comparisons_b', to='compatibility.criterion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['criterion_a', 'criterion_b'],
                'unique_together': {('user', 'criterion_a', 'criterion_b')},
            },
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Ожидает подтверждения'), ('accepted', 'Принято'), ('declined', 'Отклонено')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_requests', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('from_user', 'to_user')},
            },
        ),
        migrations.CreateModel(
            name='CriterionWeight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField()),
                ('consistency_ratio', models.FloatField(default=0.0)),
                ('criterion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compatibility.criterion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'criterion')},
            },
        ),
    ]
