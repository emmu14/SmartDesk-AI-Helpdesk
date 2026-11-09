from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Role(models.TextChoices):
        EMPLOYEE = "employee", "Employee"
        AGENT = "agent", "Support Agent"
        ADMIN = "admin", "Administrator"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )

    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )


    last_assigned_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username