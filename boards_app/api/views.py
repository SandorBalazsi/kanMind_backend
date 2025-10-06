from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from boards_app.api.serializers import BoardSerializer
from boards_app.models import Board
# Create your views here.

@api_view(['GET','POST'])
def boards_view(request):
    if request.method == 'GET':
        boards = Board.objects.all()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)