from djongo import models

class User(models.Model):
    _id = models.ObjectIdField(primary_key=True, auto_created=True)  # MongoDB auto-generated _id
    name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default='user')
    profile_pic = models.URLField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    premium_expired_at = models.DateTimeField(null=True, blank=True)
    isHidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name