from rest_framework import serializers

from .models import Category, Post, Heading


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


class PostSerializers(serializers.ModelSerializer):
    category = CategoryListSerializers()
    class Meta:
        model = Post
        fields = "__all__"

            
class PostListSerializers(serializers.ModelSerializer):
    category = CategoryListSerializers()
    class Meta:
        model = Post
        fields = ["id", 
                "title", 
                "description", 
                "thumbnail", 
                "slug", 
                "category", 
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