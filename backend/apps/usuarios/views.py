from rest_framework import generics, permissions

from .serializers import RegistroSerializer, UserSerializer


class RegistroView(generics.CreateAPIView):
    """POST /api/v1/auth/registro/ — alta de un cliente."""

    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    """GET /api/v1/auth/me/ — datos del usuario autenticado."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
