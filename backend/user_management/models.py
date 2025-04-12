from django.db import models
from datetime import datetime

class User(models.Model):
    name = models.CharField(max_length=255)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50, null=True, blank=True)
    profile_pic = models.URLField(null=True, blank=True)
    update_at = models.DateTimeField(auto_now=True)  # Automatically updates on save
    premium_expired_at = models.DateTimeField(null=True, blank=True)
    isHidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name