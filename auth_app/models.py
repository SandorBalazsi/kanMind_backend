
from django.db import models

class User(models.Model):
    email =  models.CharField(max_length=250)
    fullname = models.CharField(max_length=250)
    
    def __str__(self):
        return self.fullname

