from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email =  models.CharField(max_length=250, unique=True)
    fullname = models.CharField(max_length=250)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'fullname']
    
    def __str__(self):
        return self.fullname
    

