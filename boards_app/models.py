"""Models for board, task, and comment management.

Defines the data structures for:
  - Board: Collaborative workspace containing tasks.
  - Task: Individual work item with status, priority, and assignees.
  - Comment: Feedback or discussion on tasks.
"""

from django.db import models
from django.utils import timezone
from auth_app import models as Auth_User 

class Board(models.Model):
    """Collaborative workspace for managing tasks.

    Represents a board that contains multiple tasks and members.
    A board has an owner and can have multiple members with collaborative access.

    Attributes:
        title (CharField): Name of the board (max 250 characters).
        owner (ForeignKey): User who owns and created the board.
        members (ManyToManyField): Users who are members of this board.
        created_at (DateTimeField): Timestamp when the board was created.
        updated_at (DateTimeField): Timestamp when the board was last updated.

    Properties:
        member_count (int): Number of members on the board.
        ticket_count (int): Total number of tasks on the board.
        tasks_to_do_count (int): Number of tasks with 'to-do' status.
        tasks_high_prio_count (int): Number of tasks with 'high' priority.
    """
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
    """Individual work item on a board.

    Represents a task or ticket with a title, description, status, and priority.
    Tasks can be assigned to users and reviewed by other users.

    Status choices:
        - to-do: Task not yet started.
        - in-progress: Task is currently being worked on.
        - review: Task is awaiting review.
        - done: Task is completed.

    Priority choices:
        - low: Low priority.
        - medium: Medium priority (default).
        - high: High priority.

    Attributes:
        board (ForeignKey): Board that contains this task.
        title (CharField): Task title (max 250 characters).
        description (TextField): Detailed task description (optional).
        status (CharField): Current task status (default: 'to-do').
        priority (CharField): Task priority level (default: 'medium').
        assignee (ForeignKey): User assigned to complete the task (optional).
        reviewer (ForeignKey): User responsible for reviewing the task (optional).
        due_date (DateField): Task deadline (optional).
        created_at (DateTimeField): Timestamp when the task was created.
        updated_at (DateTimeField): Timestamp when the task was last updated.

    Properties:
        comments_count (int): Number of comments on the task.
    """
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
    """Comment or feedback on a task.

    Represents a user's comment on a task, enabling team discussion and feedback.
    Comments are automatically ordered by creation date (newest first).

    Attributes:
        task (ForeignKey): Task that the comment is attached to.
        author (ForeignKey): User who wrote the comment.
        content (TextField): The comment text content.
        created_at (DateTimeField): Timestamp when the comment was created.

    Meta:
        ordering: Comments are ordered by creation date in descending order (newest first).
    """
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
