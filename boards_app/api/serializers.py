from rest_framework import serializers
from boards_app.models import Board, Task, Comment
from auth_app.api.serializers import UserSerializer


class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserSerializer(many=True, read_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner', 'owner_id', 'members', 'member_ids',
            'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count',
            'tasks', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'created_at', 'updated_at'
        ]

    def get_tasks(self, obj):
        return TaskSerializer(obj.tasks.all(), many=True).data
    
    def create(self, ted_data):
        member_ids = ted_data.pop('member_ids', [])
        board = Board.objects.create(**ted_data)
        if member_ids:
            board.members.set(member_ids)
        board.members.add(board.owner)
        return board
    
    def update(self, instance, ted_data):
        member_ids = ted_data.pop('member_ids', None)
        instance = super().update(instance, ted_data)
        if member_ids is not None:
            instance.members.set(member_ids)
            instance.members.add(instance.owner)
        return instance
    
    
class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    board = serializers.IntegerField(write_only=True, required=True)
    board_id = serializers.IntegerField(source='board.id', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'board', 'board_id', 'title', 'description', 'status', 'priority',
            'assignee', 'assignee_id', 'reviewer', 'reviewer_id',
            'due_date', 'comments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'board', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.fullname', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'task', 'author', 'created_at']

