from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Post
from .serializers import PostListSerializers, PostSerializers


class PostListView(ListAPIView):
    queryset = Post.postobjects.all()
    serializer_class = PostListSerializers
    
class PostDetailView(RetrieveAPIView):
    queryset = Post.postobjects.all()
    serializer_class = PostSerializers
    lookup_field = "slug"
    