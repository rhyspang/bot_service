from django.contrib.auth.models import User
# ViewSets define the view behavior.
from rest_framework import viewsets

from user.serializers import UserSerializer


# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
