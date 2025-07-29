from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    dob = models.DateField()
    state = models.CharField(max_length=100)
    # engine_issue_type = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
