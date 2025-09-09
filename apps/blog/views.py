from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response 
from rest_framework.exceptions import NotFound, APIException
from django.conf import settings
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


class PostListView(APIView):
    def get(self, request, *args, **kwargs):
        """"Funcion donde te permite listar los posts, se toman todos los posts y se serializan"""
        try:
            posts = Post.objects.all()
            
            if not posts.exists():
                raise NotFound(detail="no posts found")
            
            
            for post in posts:
                redis_client.incr(f"post:impressions:{post.id}")
                
            serialized_posts = PostListSerializers(posts, many=True).data
            

        except Post.DoesNotExist:
            raise NotFound(detail="No post found")
        except Exception as e:
            raise APIException(detail=F"An unexpected error ocurred: {str(e)}")
        
        return Response(serialized_posts)

    
class PostDetailView(RetrieveAPIView):
    def get(self, request, slug):
        """Funcion donde te permite ver el detalle de un post, se toma el slug del post y se serializa"""
        try:
            post = Post.postobjects.get(slug=slug)
        except Post.DoesNotExist:
            raise NotFound(detail="The requested post do not exist")
        except Exception as e:
            raise APIException(detail=f"An unexpected error ocurred: {str(e)}")
        serialized_post = PostSerializers(post).data
        
        # Incrementa la vista del post
        try:
            post_analitics = PostAnalitics.objects.get(post=post)
            post_analitics.increment_view(request)
        except PostAnalitics.DoesNotExist:
            raise NotFound(detail="Analytics dat for this post does not exist")
        except Exception as e:
            raise APIException(detail=f"An unexpected error ocurred while updating post analytics: {str(e)}")
        return Response(serialized_post)


class PostHeadingsView(ListAPIView):
    
    serializer_class = HeadingSerializers
    
    def get_queryset(self):
        post_slug = self.kwargs.get("slug")
        return Heading.objects.filter(post__slug=post_slug)


class IncrementPostClickView(APIView):
    
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
        
        return Response({
            "Message": "Click incremented succesfully",
            "clicks" : post_analitics.clicks
        })