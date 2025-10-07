from core.permissions import HasValidAPIKEY
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework_api.views import StandardAPIView 
from rest_framework import permissions
from rest_framework.response import Response 
from rest_framework.exceptions import NotFound, APIException
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .utils import get_client_ip
from .tasks import increment_posts_views_task
import redis


from .models import Post, Heading, PostView, PostAnalitics
from .serializers import PostListSerializers, PostSerializers, HeadingSerializers
from .utils import get_client_ip
from .tasks import increment_post_impressions

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)


# class PostListView(ListAPIView):
#     queryset = Post.postobjects.all()
#     serializer_class = PostListSerializers


# class PostDetailView(RetrieveAPIView):
#     queryset = Post.postobjects.all()
#     serializer_class = PostSerializers
#     lookup_field = "slug"


class PostListView(StandardAPIView):
    permission_classes = [HasValidAPIKEY]
    #metodo decorativo para que se actualice la informacion en 1 min
    def get(self, request, *args, **kwargs):
        """"Funcion donde te permite listar los posts, se toman todos los posts y se serializan"""
        try:
            #Verificacion si los datos estan en cache
            cached_posts = cache.get("post_list")
            if cached_posts:
                #incrementa impresiones en Redis para los posts del cache
                for post in cached_posts:
                    redis_client.incr(f"post:impressions:{post['id']}")
                return self.paginate_response_with_extra(request ,cached_posts, extra_data="Informacion extra para los posts")
            
            #obrenemos los post de la base de datos si no estan en cache
            posts = Post.postobjects.all()
            
            if not posts.exists():
                raise NotFound(detail="no posts found")
                
            # Serializamos los datos
            serialized_posts = PostListSerializers(posts, many=True).data
            
            # Guardar los datos en el cache
            cache.set("post_list", serialized_posts,timeout=60 * 5)
            
            for post in posts:
                redis_client.incr(f"post:impressions:{post.id}")

        except Post.DoesNotExist:
            raise NotFound(detail="No post found")
        except Exception as e:
            raise APIException(detail=F"An unexpected error ocurred: {str(e)}")
        
        return self.paginate_response_with_extra(request, serialized_posts, extra_data="Informacion extra para los posts")

    
class PostDetailView(StandardAPIView):
    permission_classes = [HasValidAPIKEY]

    def get(self, request):
        """Funcion donde te permite ver el detalle de un post, se toma el slug del post y se serializa"""
        ip_address = get_client_ip(request)
        
        slug = request.query_params.get("slug")
        
        try:
            #Verificar que los datos esten en cache
            cached_posts = cache.get(f"post_detail:{slug}")
            if cached_posts:
                #incrementamos las vistas de post
                increment_posts_views_task.delay(slug=slug, ip_address=ip_address)
                return Response(cached_posts)
            #si no esta  en cache, obtener el post en la base de datos
            post = Post.postobjects.get(slug=slug)
            #Serializamos el post
            serialized_post = PostSerializers(post).data
            
            #Guardamos 
            cache.set(f"post_detail:{slug}", serialized_post, timeout=60*5)
            #Incrementamos las vista con la tarea en segundo plano de celery
            increment_posts_views_task.delay(post.slug, ip_address)
                        
              
        except Post.DoesNotExist:
            raise NotFound(detail="The requested post do not exist")
        except Exception as e:
            raise APIException(detail=f"An unexpected error ocurred: {str(e)}")
        return self.response(serialized_post)
    
    
class PostHeadingsView(StandardAPIView):
    permission_classes = [HasValidAPIKEY]
    def get(self, request):
        post_slug = request.query_params.get("slug")
        heading_objects = Heading.objects.filter(post__slug=post_slug)
        serialized_data = HeadingSerializers(heading_objects, many=True).data
        return self.response(serialized_data)
    # serializer_class = HeadingSerializers
    # def get_queryset(self):
    #     post_slug = self.kwargs.get("slug")
    #     return Heading.objects.filter(post__slug=post_slug)


class IncrementPostClickView(StandardAPIView):
    permission_classes = [HasValidAPIKEY]
    def post(self, request):
        """ 
        Incrementa el contador de clicks de un post basado en su slug
        """
        data = request.data
        try:
            post = Post.postobjects.get(slug=data["slug"])
        except Post.DoesNotExist:
            raise NotFound(detail="The requested post do not exist")

        try:
            post_analitics, created = PostAnalitics.objects.get_or_create(post=post)
            post_analitics.increment_click()
        except Exception as e:
            raise APIException(detail=f"An unexpected error ocurred while updating post analytics: {str(e)}")
        
        return self.response({
            "Message": "Click incremented succesfully",
            "clicks" : post_analitics.clicks
        })