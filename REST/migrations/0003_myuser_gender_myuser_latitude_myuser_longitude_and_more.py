# Generated by Django 4.2.5 on 2023-09-13 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('REST', '0002_myuser_date_of_birth_myuser_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='gender',
            field=models.CharField(choices=[('M', 'Mężczyzna'), ('F', 'Kobieta')], default='M', max_length=1),
        ),
        migrations.AddField(
            model_name='myuser',
            name='latitude',
            field=models.FloatField(default=55),
        ),
        migrations.AddField(
            model_name='myuser',
            name='longitude',
            field=models.FloatField(default=55),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='date_of_birth',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='firstName',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='lastName',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='profile_picture',
            field=models.TextField(blank=True),
        ),
    ]