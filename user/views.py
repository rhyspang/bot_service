from django.contrib.auth.models import User
# ViewSets define the view behavior.
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = User.objects.filter(username=request.user).first()
    user_serializer = UserSerializer(user, context={'request': request})
    return Response(user_serializer.data)
