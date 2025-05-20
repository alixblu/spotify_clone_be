from django.db import models
from user_management.models import User

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    payment_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ipn_data = models.JSONField(null=True, blank=True)  # Store PayPal IPN data

    class Meta:
        db_table = "payments"
        ordering = ['-created_at']
    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"
    