from django.db import models
from django.utils import timezone
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
    
    @property
    def member_count(self):
        return self.members.count()
    
    @property
    def ticket_count(self):
        return self.tasks.count()
    
    @property
    def tasks_to_do_count(self):
        return self.tasks.filter(status='to-do').count()
    
    @property
    def tasks_high_prio_count(self):
        return self.tasks.filter(priority='high').count()
    
    
class Task(models.Model):
    STATUS_CHOICES = [
        ('to-do','To Do'),
        ('in-progress','In Progress'),
        ('review','Review'),
        ('done','Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-do')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(Auth_User.User, on_delete=models.CASCADE,null=True,blank=True,related_name='assigned_tasks')
    reviewer = models.ForeignKey(Auth_User.User, on_delete=models.CASCADE,null=True,blank=True,related_name='review_tasks')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    @property
    def comments_count(self):
        return self.comments.count()
    

class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        Auth_User.User,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.fullname} on {self.task.title}"
