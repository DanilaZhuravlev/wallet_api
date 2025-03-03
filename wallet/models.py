#models.py
import uuid
from django.db import models
from django.db.models import CASCADE
from django.contrib.auth.models import User


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")

    class Meta:
        indexes = [
            models.Index(fields=['user']),  # Индекс на внешний ключ user
            models.Index(fields=['balance']),
            models.Index(fields=['id']),  # Индекс на поле balance
        ]

    def __str__(self):
        return f"Кошелёк {self.user.username} - Баланс: {self.balance}"

