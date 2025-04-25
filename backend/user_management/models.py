import bcrypt
from djongo import models

class User(models.Model):
    _id = models.ObjectIdField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords
    role = models.CharField(max_length=50, default='user')
    profile_pic = models.URLField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    premium_expired_at = models.DateTimeField(null=True, blank=True)
    isHidden = models.BooleanField(default=False)

    class Meta:
        db_table = "users"
        
    def save(self, *args, **kwargs):
        if not self.password.startswith("$2b$"):
            self.password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    def __str__(self):
        return self.name