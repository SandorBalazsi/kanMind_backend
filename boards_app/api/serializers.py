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