
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import BlogPost, Comment
from .serializers import BlogPostSerializer, CommentSerializer




class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

    @action(detail=False, methods=['get'])
    def recent(self, request):
        recent_posts = BlogPost.objects.order_by('-published_date')[:5]
        serializer = self.get_serializer(recent_posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        # Simulación: los últimos 5 como "populares"
        popular_posts = BlogPost.objects.order_by('-published_date')[:5]
        serializer = self.get_serializer(popular_posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        post = self.get_object()
        post.is_published = True
        post.save()
        return Response({'status': 'publicado'}, status=status.HTTP_200_OK)
    
    
    
    

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer