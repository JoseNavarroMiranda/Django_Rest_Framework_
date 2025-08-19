from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Post, Heading, PostView
from .serializers import PostListSerializers, PostSerializers, HeadingSerializers
from rest_framework.views import APIView
from rest_framework.response import Response 
from .utils import get_client_ip

# class PostListView(ListAPIView):
#     queryset = Post.postobjects.all()
#     serializer_class = PostListSerializers


class PostListView(APIView):
    def get(self, request, *args, **kwargs):
        """"Funcion donde te permite listar los posts, se toman todos los posts y se serializan"""
        posts = Post.objects.all()
        serialized_posts = PostListSerializers(posts, many=True).data
        return Response(serialized_posts)

    
# class PostDetailView(RetrieveAPIView):
#     queryset = Post.postobjects.all()
#     serializer_class = PostSerializers
#     lookup_field = "slug"

    
class PostDetailView(RetrieveAPIView):
    def get(self, request, slug):
        """Funcion donde te permite ver el detalle de un post, se toma el slug del post y se serializa"""
        post = Post.postobjects.get(slug=slug)
        serialized_post = PostSerializers(post).data
        
        client_ip = get_client_ip(request)
        
        if PostView.objects.filter(post=post, ip_address=client_ip).exists():
            return Response(serialized_post)
        
        PostView.objects.create(post=post, ip_address = client_ip)
        
        return Response(serialized_post)


class PostHeadingsView(ListAPIView):
    
    serializer_class = HeadingSerializers
    
    def get_queryset(self):
        post_slug = self.kwargs.get("slug")
        return Heading.objects.filter(post__slug=post_slug)
    