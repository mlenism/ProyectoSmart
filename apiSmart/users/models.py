from django.db import models
from django.contrib.auth.models import User

class Description(models.Model):
    description_desc = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='descriptions')
    
    def owner_username(self):
        return self.owner.username

    def owner_email(self):
        return self.owner.email