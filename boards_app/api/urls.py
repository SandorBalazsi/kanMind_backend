from django.urls import path
from . import views

urlpatterns = [
    # Boards
    path('boards/', views.BoardViewSet.as_view({'get': 'list', 'post': 'create'}), name='board-list'),
    path('boards/<int:pk>/', views.BoardViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='board-detail'),
    path('boards/<int:pk>/add_member/', views.BoardViewSet.as_view({'post': 'add_member'}), name='board-add-member'),
    path('boards/<int:pk>/remove_member/', views.BoardViewSet.as_view({'post': 'remove_member'}), name='board-remove-member'),

    # Tasks
    path('boards/<int:board_id>/tasks/', views.TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-list'),
    path('boards/<int:board_id>/tasks/<int:pk>/', views.TaskViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='task-detail'),
    path('boards/<int:board_id>/tasks/assigned/', views.TaskViewSet.as_view({'get': 'assigned'}), name='task-assigned'),
    path('boards/<int:board_id>/tasks/reviewer/', views.TaskViewSet.as_view({'get': 'reviewer'}), name='task-reviewer'),
    path('boards/<int:board_id>/tasks/<int:pk>/comments/', views.TaskViewSet.as_view({'get': 'comments', 'post': 'comments'}), name='task-comments'),

    # Comments
    path('boards/<int:board_id>/tasks/<int:task_id>/comments/', views.CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='comment-list'),
    path('boards/<int:board_id>/tasks/<int:task_id>/comments/<int:pk>/', views.CommentViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='comment-detail'),
]
