from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    is_private = models.BooleanField(default=False)
    
    # Nuevo campo para autor (relación con User)
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,    # Permite NULL en la BD
        blank=True,    # Permite vacío en el admin
    )

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(
        BlogPost, 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario en: {self.post.title}"