from django.db import models
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import AbstractUser


class Sites(models.Model):
    name = models.CharField(max_length=128)
    url = models.URLField(max_length=256)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
