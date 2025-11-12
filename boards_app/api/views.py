from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import models
from boards_app.models import Board, Task, Comment
from .serializers import BoardSerializer, TaskSerializer, CommentSerializer
from .permissions import IsBoardOwnerOrMember, IsTaskBoardMember



# --- BOARDS ---
class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsBoardOwnerOrMember]

    def get_queryset(self):
        return Board.objects.filter(
            models.Q(owner=self.request.user) | models.Q(members=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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

    def get_queryset(self):
        from django.db.models import Q

        accessible_boards = Board.objects.filter(
            Q(owner=self.request.user) | Q(members=self.request.user)
        ).distinct()

        queryset = Task.objects.filter(board__in=accessible_boards)

        board_id = self.kwargs.get('board_id')
        if board_id:
            queryset = queryset.filter(board_id=board_id)

        return queryset

    def perform_create(self, serializer):
        board_id = self.request.data.get('board')
        print("DEBUG board_id:", board_id)

        if not board_id:
            raise ValidationError({'error': 'board is required.'})

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise ValidationError({'error': 'Board not found.'})

        serializer.save(board=board)


    @action(detail=False, methods=['get'])
    def assigned(self, request, board_id=None):
        """Get tasks assigned to current user."""
        tasks = self.get_queryset().filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reviewer(self, request, board_id=None):
        """Get tasks where current user is reviewer."""
        tasks = self.get_queryset().filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, board_id=None, pk=None):
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
        """Return comments only for accessible boards and optionally filter by task_id."""
        from django.db.models import Q

        accessible_boards = Board.objects.filter(
            Q(owner=self.request.user) | Q(members=self.request.user)
        ).distinct()

        queryset = Comment.objects.filter(task__board__in=accessible_boards)

        task_id = self.kwargs.get('task_id')
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        return queryset

    def perform_create(self, serializer):
        """Attach comment to correct task."""
        task_id = self.kwargs.get('task_id')
        serializer.save(author=self.request.user, task_id=task_id)
