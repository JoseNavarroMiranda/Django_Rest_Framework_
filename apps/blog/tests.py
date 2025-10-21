from django.test import TestCase
from .models import Category, Post, PostAnalitics, Heading
from django.urls import reverse
from rest_framework.test import APIClient
from django.conf import settings
# Create your tests here.

#Class tests
class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            title= "esto es una prueba",
            description="all about testing",
            slug="test"
        )
    
    def test_category_creation(self):
        self.assertEqual(str(self.category), "Test Category")
        self.assertEqual(self.category.title, "esto es una prueba")
      
      
class PostModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            title= "esto es una prueba",
            description="all about testing",
            slug="test"
        )
        self.post = Post.objects.create(
            category=self.category,
            title="Test Post",
            slug="test-post",
            content="This is a test post content.",
            description="Test Description",
            keywords="test,post",
            status = 'published',
            thumbnail=None,
        )
    def test_post_creation(self):
        self.assertEqual(str(self.post), "Test Post")
        self.assertEqual(self.post.category.name, "Test Category")
    
    def test_post_published_manager(self):
        self.assertTrue(Post.postobjects.filter(status='published').exists())
        

#Views tests

class PostListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name = "API", title = "API Testing",)
        self.api_key = settings.VALID_API_KEYS[0]
        self.post = Post.objects.create(
            title = "API Post",
            slug = "api-post",
            content = "Content for API post",
            description = "API Post Description",
            category = self.category,
            status = 'published',
        )
        
    def test_get_posts(self):
        url = reverse ('post-list')
        response = self.client.get(
            url,
            HTTP_API_KEY=self.api_key
            )
        
        print(response.json())  # Imprime los datos de la respuesta para depuración
        
        data = response.json()
        
        self.assertIn('success', data )
        self.assertTrue(data['success'])
        self.assertIn('status', data )
        self.assertEqual(data['status'], 200)
        self.assertIn('results', data)
        self.assertEqual(data['count'], 1)
        
        results = data['results']
        self.assertEqual(len(results), 1)
        
        post_data = results[0]