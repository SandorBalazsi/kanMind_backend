from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.db import models
from boards_app.models import Board, Task, Comment
from .serializers import BoardSerializer,BoardListSerializer, BoardUpdateResponseSerializer, BoardUpdateSerializer, TaskSerializer, CommentSerializer
from .permissions import IsBoardOwnerOrMember, IsTaskBoardMember



# --- BOARDS ---
class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer, BoardListSerializer
    permission_classes = [IsBoardOwnerOrMember]
    lookup_url_kwarg = 'board_id'

    def get_serializer_class(self):
        if self.action == 'list':
            return BoardListSerializer
        return BoardSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            board = serializer.instance
            response_serializer = BoardListSerializer(board)
        
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except ValidationError as e:
        
            return Response(
                {
                    'error': 'Invalid request data',
                    'details': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
        except Exception as e:
        
            return Response(
                {
                    'error': 'Internal Server Error',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_queryset(self):
        queryset = Board.objects.filter(members=self.request.user)
        
        if self.action == 'list':
            queryset = queryset.prefetch_related('members', 'tasks')
        else:
            queryset = queryset.prefetch_related(
                'members',
                'tasks__assignee',
                'tasks__reviewer'
            )
        
        return queryset
    
    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        board_id = self.kwargs[lookup_url_kwarg]
        
        try:
            obj = self.get_queryset().get(id=board_id)
        except Board.DoesNotExist:
            raise PermissionDenied("You do not have permission to access this board.")
        
        self.check_object_permissions(self.request, obj)
        
        return obj

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BoardUpdateSerializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = BoardUpdateResponseSerializer(instance)
        return Response(response_serializer.data)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        board = self.get_object()
        member_id = request.data.get('member_id')

        if not member_id:
            return Response({'error': 'member_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from auth_app.models import User
            member = User.objects.get(id=member_id)
            board.members.add(member)
            return Response({'message': 'Member added successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        board = self.get_object()
        member_id = request.data.get('member_id')

        if not member_id:
            return Response({'error': 'member_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from auth_app.models import User
            member = User.objects.get(id=member_id)
            if member == board.owner:
                return Response({'error': 'Cannot remove board owner'}, status=status.HTTP_400_BAD_REQUEST)
            board.members.remove(member)
            return Response({'message': 'Member removed successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# --- TASKS ---
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsTaskBoardMember]
    
    lookup_field = "id"
    lookup_url_kwarg = 'task_id'

    def get_queryset(self):
        return Task.objects.select_related(
            'board', 'assignee', 'reviewer'
        ).prefetch_related('comments')
    
    def get_object(self):

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        task_id = self.kwargs[lookup_url_kwarg]
        
        try:
            obj = self.get_queryset().get(id=task_id)
        except Task.DoesNotExist:
            raise PermissionDenied("You do not have permission to access this task.")
        
        self.check_object_permissions(self.request, obj)
        
        return obj
    

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        """GET /api/tasks/assigned-to-me/"""
        tasks = self.get_queryset().filter(assignee_id=request.user.id)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        """GET /api/tasks/reviewing/"""
        tasks = self.get_queryset().filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, task_id=None, pk=None):
        """GET or POST comments for a task."""
        task = self.get_object()

        if request.method == 'GET':
            comments = task.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(task=task, author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='boards/tasks')
    def create_task_with_board_in_body(self, request):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- COMMENTS ---
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsTaskBoardMember]
    
    def get_queryset(self):
        from django.db.models import Q
        
        accessible_boards = Board.objects.filter(
            Q(owner=self.request.user) | Q(members=self.request.user)
        ).distinct()
        
        task_id = self.kwargs.get('task_id')
        return Comment.objects.filter(
            task__board__in=accessible_boards,
            task_id=task_id
        )
    
    def get_object(self):
        comment_id = self.kwargs.get('pk')
        task_id = self.kwargs.get('task_id')

        try:
            obj = self.get_queryset().get(id=comment_id, task_id=task_id)
        except Comment.DoesNotExist:

            raise PermissionDenied("You do not have permission to access this comment.")
        
        self.check_object_permissions(self.request, obj)
        
        return obj
    
    def list(self, request, *args, **kwargs):
        task_id = self.kwargs.get('task_id')
        
        from django.db.models import Q
        accessible_boards = Board.objects.filter(
            Q(owner=request.user) | Q(members=request.user)
        ).distinct()
        
        task_exists = Task.objects.filter(
            id=task_id,
            board__in=accessible_boards
        ).exists()
        
        if not task_exists:
            raise PermissionDenied("You do not have permission to access this task.")
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_id')
        serializer.save(author=self.request.user, task_id=task_id)