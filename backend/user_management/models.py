from django.db import models

# Create your models here.
from datetime import datetime, timedelta
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, default='user')  # 'admin' or 'user'
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(null=True, blank=True)

    def activate_premium(self):
        current_time = datetime.now()
        if self.premium_expires_at and current_time < self.premium_expires_at:
            return False  # Premium already active
        self.is_premium = True
        self.premium_expires_at = current_time + timedelta(hours=24)
        self.save()
        return True