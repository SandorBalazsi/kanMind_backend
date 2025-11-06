from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from boards_app.models import Board
from .serializers import BoardSerializer
from .permissions import IsBoardOwnerOrMember

class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsBoardOwnerOrMember]
    
    def get_queryset(self):
        return Board.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(members=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        board = self.get_object()
        member_id = request.data.get('member_id')
        
        if not member_id:
            return Response(
                {'error': 'member_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from auth_app.models import User
            member = User.objects.get(id=member_id)
            board.members.add(member)
            return Response({'message': 'Member added successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        board = self.get_object()
        member_id = request.data.get('member_id')
        
        if not member_id:
            return Response(
                {'error': 'member_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from auth_app.models import User
            member = User.objects.get(id=member_id)
            if member == board.owner:
                return Response(
                    {'error': 'Cannot remove board owner'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            board.members.remove(member)
            return Response({'message': 'Member removed successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )