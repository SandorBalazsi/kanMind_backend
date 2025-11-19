from rest_framework import serializers
from boards_app.models import Board, Task, Comment
from auth_app.api.serializers import UserSerializer
from auth_app.models import User


class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner_id', 'members','tasks'
        ]
        read_only_fields = [
            'id', 'owner_id'
        ]

    def get_tasks(self, obj):
        return TaskSerializer(
            obj.tasks.all(), 
            many=True, 
            context={'nested_in_board': True}
        ).data
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['members'] = UserSerializer(instance.members.all(), many=True).data
        return representation
    
    def create(self, validated_data):
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        board.members.add(board.owner)
        return board
    
    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        instance = super().update(instance, validated_data)
        if members is not None:
            instance.members.set(members)
            instance.members.add(instance.owner)
        return instance
    

class BoardListSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id'
        ]
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()
    
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()
    
    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()
    
class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        model = Board
        fields = ['title', 'members']
    
class BoardUpdateResponseSerializer(serializers.ModelSerializer):
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']
    
class TaskSerializer(serializers.ModelSerializer):
    board_id = serializers.SerializerMethodField(read_only=True)
    board = serializers.IntegerField(write_only=True, required=True)
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    comments_count = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Task
        fields = [
            'id',
            'board_id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'assignee_id',
            'reviewer',
            'reviewer_id',
            'due_date',
            'comments_count'
        ]
        read_only_fields = ['id', 'board_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.context.get('nested_in_board'):
            self.fields.pop('board_id', None)
            self.fields.pop('board', None)
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def create(self, validated_data):
        board_id = validated_data.pop('board')
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)
        
        board = Board.objects.get(id=board_id)
        task = Task.objects.create(board=board, **validated_data)
        
        if assignee_id:
            task.assignee_id = assignee_id
        if reviewer_id:
            task.reviewer_id = reviewer_id
        
        task.save()
        return task


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.fullname', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'task', 'author', 'created_at']

