from django.db import models
from django.db.models import Q 
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
        queryset = BlogPost.objects.filter(is_archived=False)

        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                models.Q(is_private=False) | models.Q(author=self.request.user)
            )
        else:
            queryset = queryset.filter(is_private=False)
        
        return queryset

    @action(detail=False, methods=['get'])
    def recent(self, request):
        recent_posts = BlogPost.objects.order_by('-published_date')[:5]
        serializer = self.get_serializer(recent_posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
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
            post.is_featured = False
            post.save()
            return Response({'status': 'Post ya no está destacado'}, status=status.HTTP_200_OK)
        else:
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
    @action(detail=True, methods=['post'])
    def make_private(self, request, pk=None):
        try:
            post = BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Post no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if post.is_private:
            post.is_private = False
            post.save()
            return Response({'status': 'Post es ahora público'}, status=status.HTTP_200_OK)
        else:

            post.is_private = True
            post.save()
            return Response({'status': 'Post es ahora privado'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def search(self, request):
        keyword = request.query_params.get('keyword', None)
        
        if not keyword:
            return Response(
                {'error': 'Debes proporcionar una palabra clave con el parámetro "keyword"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        posts = BlogPost.objects.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword),
            is_archived=False
        )
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        try:
            post = BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Post no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        summary_text = post.content[:100]
        if len(post.content) > 100:
            summary_text += "..."
        
        return Response(
            {
                'id': post.id,
                'title': post.title,
                'summary': summary_text,
                'published_date': post.published_date
            },
            status=status.HTTP_200_OK
        )
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Debes estar autenticado para ver tus posts'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        

        posts = BlogPost.objects.filter(author=request.user, is_archived=False)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer