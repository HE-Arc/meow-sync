import rest_framework.viewsets
from .models import Comment
from .serializers import CommentSerializer


class CommentViewSet(rest_framework.viewsets.ModelViewSet):
	queryset = Comment.objects.all()
	serializer_class = CommentSerializer
