from django.db import models
from auth_app import models as Auth_User 

# Create your models here.
class Board(models.Model):
    title = models.CharField(max_length=250)
    owner = models.ForeignKey(Auth_User.User,on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(Auth_User.User, related_name='boards', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title