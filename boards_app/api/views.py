"""ViewSets for board, task, and comment API endpoints.

Provides REST API endpoints for CRUD operations on boards, tasks, and comments
with comprehensive permission and authentication checks.
"""

from urllib import request
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound, NotAuthenticated
from boards_app.models import Board, Task, Comment
from .serializers import BoardSerializer,BoardListSerializer, BoardUpdateResponseSerializer, BoardUpdateSerializer, TaskSerializer, CommentSerializer
from .permissions import IsBoardOwnerOrMember, IsTaskBoardMember


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer, BoardListSerializer
    permission_classes = [IsBoardOwnerOrMember]
    lookup_url_kwarg = 'board_id'

    def get_serializer_class(self):
        if self.action == 'list':
            return BoardListSerializer
        return BoardSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a board and return list-style representation.

        This override validates input, creates the board (owner set in
        `perform_create`) and returns the `BoardListSerializer` representation
        for the created board. Errors are caught and mapped to appropriate
        HTTP responses.
        """
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
        """Return boards accessible to the requesting user.

        Lists boards where the request user is a member. The queryset is
        prefetched differently for list/detail views to optimize related lookups.
        """
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
        """Retrieve a board by id without restricting to the member-filtered
        queryset, then enforce object permissions.

        This allows returning `403 Forbidden` when a board exists but the
        user isn't a member, while a non-existent board raises `404`.
        """
        board_id = self.kwargs['board_id']

        try:
            obj = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board not found.")

        self.check_object_permissions(self.request, obj)

        return obj

    def perform_create(self, serializer):
        """Save a new board setting the request user as owner and member."""
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """Apply a partial update to a board using `BoardUpdateSerializer`.

        Returns the updated board using `BoardUpdateResponseSerializer`.
        """
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
        """Add a user to the board members list by id in request body.

        Validates presence of `member_id` and returns 404 if the user
        cannot be found.
        """
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
        """Remove a member from a board, preventing removal of the owner."""
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
        """Retrieve a task by id and enforce object permissions.

        Fetches the task with its board relation and raises `404` if not
        found. Object permissions are then checked to return `403` when
        appropriate.
        """
        task_id = self.kwargs['task_id']

        try:
            obj = Task.objects.select_related('board').get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        self.check_object_permissions(self.request, obj)

        return obj
    

    def perform_create(self, serializer):
        """Persist a new task using serializer data (no extra logic)."""
        serializer.save()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        """Return tasks where the authenticated user is the assignee."""
        tasks = self.get_queryset().filter(assignee_id=request.user.id)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        """Return tasks where the authenticated user is the reviewer."""
        tasks = self.get_queryset().filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, task_id=None, pk=None):
        """GET or POST comments for a specific task.

        GET: list comments for the task.
        POST: create a comment on the task and set the authenticated user
              as the author.
        """
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
        """Helper action to create a task when the board id is supplied
        in the request body.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsTaskBoardMember]
    
    def get_queryset(self):
        """
        Retrieve comments for a specific task, ensuring the user has access to the board.

        This method filters comments based on:
        1. The task ID from the URL parameters
        2. Boards that the user owns or is a member of

        Returns:
            QuerySet: A distinct queryset of Comment objects that belong to the specified task
                      and are associated with boards accessible to the current user.
        """
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
        """Retrieve a comment for a specific task and enforce permissions."""
        comment_id = self.kwargs['pk']
        task_id = self.kwargs['task_id']

        try:
            obj = Comment.objects.select_related('task__board').get(
                id=comment_id,
                task_id=task_id
            )
        except Comment.DoesNotExist:
            raise NotFound("Comment not found.")

        self.check_object_permissions(self.request, obj)

        return obj
    
    def list(self, request, *args, **kwargs):
        """List comments for a task after verifying board access."""
        task_id = self.kwargs.get('task_id')

        try:
            task = Task.objects.select_related('board').get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        board = task.board
        if board.owner != request.user and request.user not in board.members.all():
            raise PermissionDenied("You do not have permission to access this task.")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Create a comment for a task after validating board membership."""
        task_id = self.kwargs.get('task_id')

        try:
            task = Task.objects.select_related('board').get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        board = task.board
        if board.owner != request.user and request.user not in board.members.all():
            raise PermissionDenied("You do not have permission to access this task.")

        serializer.save(author=self.request.user, task_id=task_id)