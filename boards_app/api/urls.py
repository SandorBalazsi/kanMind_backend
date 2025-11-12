from django.urls import path
from . import views

urlpatterns = [

    path('boards/', views.BoardViewSet.as_view({'get': 'list', 'post': 'create'}), name='board-list'),
    path('boards/<int:pk>/', views.BoardViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='board-detail'),
    path('boards/<int:pk>/add_member/', views.BoardViewSet.as_view({'post': 'add_member'}), name='board-add-member'),
    path('boards/<int:pk>/remove_member/', views.BoardViewSet.as_view({'post': 'remove_member'}), name='board-remove-member'),

    path('tasks/assigned-to-me/', views.TaskViewSet.as_view({'get': 'assigned'}), name='task-assigned'),
    path('tasks/reviewing/', views.TaskViewSet.as_view({'get': 'reviewer'}), name='task-reviewer'),
    path('tasks/', views.TaskViewSet.as_view({'post': 'create', 'get': 'list'}), name='task-list'),
    path('tasks/<int:pk>/', views.TaskViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='task-detail'),

    
    path('tasks/<int:task_id>/comments/', views.CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='comment-list'),
    path('tasks/<int:task_id>/comments/<int:pk>/', views.CommentViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='comment-detail'),
]
