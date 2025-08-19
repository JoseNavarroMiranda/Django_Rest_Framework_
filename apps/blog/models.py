import uuid

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from apps.blog.utils import get_client_ip
from django_ckeditor_5.fields import CKEditor5Field


def blog_thumbnail_directory(instance, filename):
    """Esta funcion se utiliza para crear un directorio unico para cada imagen"""
    return "blog/{0}/{1}".format(instance.title, filename)

def category_thumbnail_directory(instance, filename):
    """Esta funcion se utiliza para crear un directorio unico para cada imagen de categoria"""
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
            """Funcion que permite filtrar a frontend solo por los post que estaran como 'published'"""
            
            return super().get_queryset().filter(status='published')
            
    status_options=(
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
        )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False )
    title = models.CharField(max_length=90)
    description = models.CharField(max_length=128)
    content = CKEditor5Field('content', config_name='default')
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
    
    #Campo que permite contar las vistas del post, de manera concecutiva sin tomar en cuenta las ips de un equipo
    # views = models.IntegerField(default=0)
    
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
    

class PostView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name='post_view' )
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

#Modelo de analiticas para la recomendaciones de los posts
class PostAnalitics(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # relaciona el post con las analiticas
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name='post_analitics')
    # campos para las analiticas
    views = models.PositiveIntegerField(default=0)
    # impresion para incrementar el conteo de vistas
    impressions = models.PositiveIntegerField(default=0)
    # Define el numero de clicks y la tasa de clics (distinta que sea vista por URL)
    clicks = models.PositiveIntegerField(default=0)
    # Tasa de clics (CTR) calculada como clicks / impresiones
    click_through_rate = models.FloatField(default=0.0)
    #Guarda el tiempo promedio que un usuario pasa en la pagina del Post
    average_time_on_page = models.FloatField(default=0.0)
  
    def increment_click(self):
        """Esta funciona incrementa el cocnteo de clicks del post"""
        self.clicks += 1
        self._update_click_through_rate()
    
    def _update_click_through_rate(self):
        """Esta funcion actualiza la tasa de clics (CTR)"""
        if self.impressions > 0:
            self.click_through_rate = (self.clicks / self.impressions) * 100
            
    def increment_impression(self):
        """Esta funcion incrementa el conteo de impresiones del post"""
        self.impressions += 1
        self._update_click_through_rate()
    
    def increment_view(self, request):
        ip_address = get_client_ip(request)
        
        if not PostView.objects.filter(post=self.post, ip_address=ip_address).exists():
            PostView.objects.create(post=self.post, ip_address=ip_address)
            self.views += 1
            self.save()

        
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