from rest_framework import serializers

from .models import Category, Post, Heading, PostView


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CategoryListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'name',
            'slug'
            ]


class HeadingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Heading
        fields = [
            "title",
            "slug",
            "level",
            "order",
        ]


class PostViewSerializers(serializers.ModelSerializer):
    class Meta:
        model = PostView
        fields = "__all__"    


class PostSerializers(serializers.ModelSerializer):
    category = CategoryListSerializers()
    headings = HeadingSerializers(many=True)       
    view_count =  serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = "__all__"
        
    def get_view_count(self, obj):
        """Este metodo permite obtener el conteo de vistas del post"""
        return obj.post_view.count()

            
class PostListSerializers(serializers.ModelSerializer):
    category = CategoryListSerializers()
    view_count =  serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ["id", 
                "title", 
                "description", 
                "thumbnail", 
                "slug", 
                "category",
                'view_count',
                ]
    def get_view_count(self, obj):
        """Este metodo permite obtener el conteo de vistas del post"""
        return obj.post_view.count()    
