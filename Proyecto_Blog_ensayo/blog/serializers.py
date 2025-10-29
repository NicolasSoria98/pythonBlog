from rest_framework import serializers
from .models import BlogPost, Comment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_date', 'post']

class BlogPostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    
    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("El título debe tener al menos 5 caracteres.")
        return value

    def validate_content(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError("El contenido debe tener al menos 20 caracteres.")
        return value   
    def validate_is_featured(self, value):
        if value:
            featured_count = BlogPost.objects.filter(is_featured=True).count()

            if self.instance and self.instance.is_featured:
                featured_count -= 1

            if featured_count >= 5:
                raise serializers.ValidationError("Ya hay 5 posts destacados. No se pueden destacar más.")
        
        return value 
    def validate_content(self, value):
        palabras_ofensivas = ['tonto', 'idiota', 'estúpido', 'imbécil']
        
        if len(value.strip()) < 20:
            raise serializers.ValidationError("El contenido debe tener al menos 20 caracteres.")
        
        contenido_lower = value.lower()
        for palabra in palabras_ofensivas:
            if palabra in contenido_lower:
                raise serializers.ValidationError(
                    f"El contenido contiene palabras no permitidas. Por favor, usa un lenguaje respetuoso."
                )
        
        return value    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'published_date','is_published', 'is_featured', 'is_archived', 'author', 'comments', 'views_count', 'is_private']

        
