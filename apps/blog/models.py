import uuid

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from ckeditor.fields import RichTextField


def blog_thumbnail_directory(instance, filename):
    # Esta funcion se utiliza para crear un directorio unico para cada imagen
    return "blog/{0}/{1}".format(instance.title, filename)

def category_thumbnail_directory(instance, filename):
    # Esta funcion se utiliza para crear un directorio unico para cada imagen de categoria
    return "blog_categories/{0}/{1}".format(instance.name, filename)

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False )
    parent = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=250)
    title = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to=category_thumbnail_directory, blank=True, null=True)
    slug = models.CharField(max_length=128)
    
    def __str__(self):
        return self.name

class Post(models.Model):
    
    class PostObjects(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status='published')
            
    status_options=(
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
        )
    title = models.CharField(max_length=90)
    description = models.CharField(max_length=128)
    content = RichTextField(blank=True, null=True)
    #donde se guardan las imagenes
    thumbnail = models.ImageField(upload_to=blog_thumbnail_directory, blank=True, null=True)
    #Keyword lo utilizo para crear un buscador de articulos
    keywords = models.CharField(max_length=128)
    #Slug lo utiliza para crear URLs amigables
    slug = models.CharField(max_length=128)
    #Campo que conecta con la categoria
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    #status del post
    status = models.CharField(
        max_length=10,
        choices=status_options,
        default='draft',)
    objects = models.Manager() #default manager
    postobjects = PostObjects() #custom manager
    
    class Meta:
        ordering = ("-created_at",)
    
    def __str__(self):
        return self.title

class Heading(models.Model):    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False )    
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name='headings')
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    level = models.IntegerField(
        choices=(
            (1, "H1"),
            (2, "H2"),
            (3, "H3"),
            (4, "H4"),
            (5, "H5"),
            (6, "H6"),
            )
    )
    order = models.PositiveIntegerField()
    
    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)