from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
# Create your models here.
User = get_user_model()


class Loans(models.Model):
    class Status(models.TextChoices):
        PAID = "PAID", "paid"
        PENDING = "PENDING", "pending"
        APPROVED = "APPROVED", "approved"
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=22, decimal_places=2, blank=True, null=True)
    status = models.CharField(
        _("Status"), max_length=50, choices=Status.choices, default=Status.PENDING)
    interest = models.FloatField()
    date_paid = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.phone_number
