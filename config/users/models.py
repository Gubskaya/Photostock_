from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uploaded_images_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Profile for {self.user.username}'