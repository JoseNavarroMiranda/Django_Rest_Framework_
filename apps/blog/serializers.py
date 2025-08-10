from rest_framework import serializers

from .models import Category, Post, Heading

class PostSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

class PostListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", 
                "title", 
                "description", 
                "thumbnail", 
                "slug", 
                "category", 
                ]
    
class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
    
class HeadingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Heading
        fields = [
            "title",
            "slug",
            "level",
            "order",
        ]