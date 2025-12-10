from django.contrib import admin
from .models import Board, Task, Comment
from auth_app.models import User

admin.site.register(User)
admin.site.register(Board)
admin.site.register(Task)
admin.site.register(Comment)
