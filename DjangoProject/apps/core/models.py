from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator



class AuthUser(AbstractUser):
    # #exclude this fields whil migrations
    # is_superuser = None
    # is_staff = None
    # last_login = None


    # username = None
    first_name = None
    last_name = None
    username = models.CharField(
        max_length=255, unique=True, db_column='username', null=False)
    password = models.CharField(
        max_length=128,
        validators=[
            MinLengthValidator(limit_value=8, message="Password must be at least 8 characters long."),
            MaxLengthValidator(limit_value=128, message="Password must be at most 128 characters long."),
            RegexValidator(
                regex='^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$',
                message="Password must contain at least one digit, one lowercase letter, one uppercase letter, and one special character."
            ),
        ]
    )
    email = models.CharField(max_length=255, unique=True,
                             db_column='email', null=True)
    first_name = models.CharField(
        max_length=255, blank=True, null=True, db_column='first_name')
    last_name = models.CharField(
        max_length=150, blank=True, null=True, db_column='last_name')
    role = models.CharField(max_length=20, db_column='role')
    date_joined = models.DateTimeField(
        auto_created=True, null=True, db_column='date_joined')
    is_active = models.BooleanField(default=True, db_column='is_active')
    is_superuser = models.BooleanField(default=False, db_column='is_superuser')
    is_staff = models.BooleanField(default=True, db_column='is_staff')
    # USERNAME_FIELD = 'username'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


    class Meta:
        managed = True
        db_table = "auth_user"
    
    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super(AuthUser, self).save(*args, **kwargs)
    
    def get_active_sessions(self):
        # Get active sessions excluding the current session
        user_sessions = Session.objects.filter(
            expire_date__gt=timezone.now(),
            session_key__contains=str(self.id)
        ).exclude(session_key=self.session.session_key)

        return user_sessions
