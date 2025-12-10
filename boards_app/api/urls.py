from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'boards', views.BoardViewSet, basename='board')
router.register(r'tasks', views.TaskViewSet, basename='task')

urlpatterns = [
    path('api/', include(router.urls)),
    
    path('api/tasks/assigned-to-me/', views.TaskViewSet.as_view({'get': 'assigned_to_me'}), name='tasks-assigned-to-me'),
    path('api/tasks/reviewing/', views.TaskViewSet.as_view({'get': 'reviewing'}), name='tasks-reviewing'),

    path('api/tasks/<int:task_id>/comments/', views.CommentViewSet.as_view({'get': 'list','post': 'create'}), name='task-comments'),
    path('api/tasks/<int:task_id>/comments/<int:pk>/', views.CommentViewSet.as_view({'delete': 'destroy'}), name='task-comment-detail'),
]