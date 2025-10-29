
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import BlogPost, Comment
from .serializers import BlogPostSerializer, CommentSerializer




class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

    def get_queryset(self):
        return BlogPost.objects.filter(is_archived=False)

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
    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        post = self.get_object()
        featured_count = BlogPost.objects.filter(is_featured=True).count()
        
        if post.is_featured:
            # Si ya está destacado, quitarlo
            post.is_featured = False
            post.save()
            return Response({'status': 'Post ya no está destacado'}, status=status.HTTP_200_OK)
        else:
            # Si no está destacado, verificar el límite
            if featured_count >= 5:
                return Response(
                    {'error': 'Ya hay 5 posts destacados. No se pueden destacar más.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            post.is_featured = True
            post.save()
            return Response({'status': 'Post destacado exitosamente'}, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_posts = BlogPost.objects.filter(is_featured=True)
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        post = self.get_object()
        
        if post.is_archived:
            post.is_archived = False
            post.save()
            return Response({'status': 'Post desarchivado'}, status=status.HTTP_200_OK)
        else:
            post.is_archived = True
            post.save()
            return Response({'status': 'Post archivado exitosamente'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='by-year/(?P<year>[0-9]{4})')
    def by_year(self, request, year=None):
        posts = BlogPost.objects.filter(
            published_date__year=year,
            is_archived=False
        )
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        try:
            post = BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Post no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        post.views_count += 1
        post.save()
        return Response(
            {
                'status': 'Vista registrada',
                'views_count': post.views_count
            },
            status=status.HTTP_200_OK
        )

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer