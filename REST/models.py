from datetime import date
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=100)
    logo_url = models.CharField(max_length=255)
    group_site_url = models.URLField(default='')

    def __str__(self):
        return self.name


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Tworzy i zapisuje użytkownika z podanym adresem e-mail, datą
        urodzenia i hasłem.
        """
        if not email:
            raise ValueError('Użytkownicy muszą posiadać adres e-mail')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    class sexType(models.TextChoices):
        MALE = 'M', _('Mężczyzna')
        FEMALE = 'F', _('Kobieta')

    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    profile_picture = models.TextField(blank=True)
    gender = models.CharField(max_length=1, choices=sexType.choices, default='M')
    latitude = models.FloatField(default=55)
    longitude = models.FloatField(default=55)
    description = models.TextField(blank=True)
    groups = models.ManyToManyField(Group, related_name='users')
    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def __str__(self):
        return self.email


class Friend(models.Model):
    person = models.ForeignKey(MyUser, on_delete=models.DO_NOTHING, related_name='person')
    friend = models.ForeignKey(MyUser, on_delete=models.DO_NOTHING, related_name='person_friends')


class Message(models.Model):
    sender = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}'
