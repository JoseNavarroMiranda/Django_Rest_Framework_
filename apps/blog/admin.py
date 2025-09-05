from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Category, Post, Heading, PostAnalitics

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'parent', 'slug',)
    search_fields = ('name', 'title', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)
    ordering = ('name',)
    readonly_fields = ('id',)
    list_editable = ('title',)


class HeadingInline(admin.TabularInline):
    model = Heading
    extrta = 1
    fields = ('title', 'level', 'order', 'slug' )
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order',)


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditor5Widget(
            config_name="default",
            attrs={
                "spellcheck": "false",
                "autocorrect": "off",
                "autocapitalize": "off",
                "data-gramm": "false",
            }
        )
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):    
    form = PostAdminForm

    class Media:
        css = {"all": ("css/ckeditor-dark.css",)}
          
    list_display = ('title', 'status', 'category', 'created_at', 'updated_at',)
    search_fields = ('title', 'description', 'content', 'keywords', 'slug',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'category', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('id','created_at', 'updated_at')
    fieldsets = (
        ('General Information', {
           'fields': ('title', 'description', 'content', 'thumbnail', 'keywords', 'slug','category') 
        }),
        ('status & Dates',{
            'fields': ('status', 'created_at', 'updated_at' )
        })
    )
    inlines = [HeadingInline]


@admin.register(Heading)
class HeadingAdmin(admin.ModelAdmin):
    list_display = ('title', 'post' ,'level', 'order')
    search_fields = ('title', 'post__title')
    list_filter = ('level', 'post')
    ordering = ('order',)
    prepopulated_fields = {'slug': ('title',)} 


@admin.register(PostAnalitics)
class PostAnaliticsAdmin(admin.ModelAdmin):
    list_display  = ('post_title', 'views', 'impressions', 'clicks', 'click_through_rate', 'average_time_on_page',)
    search_fields = ('post__title',)
    readonly_fields = ('views', 'impressions', 'clicks' , 'click_through_rate' ,'average_time_on_page',)
    
    def has_delete_permission(self, request, obj=None):
        """Funcion que permite deshabilitar la opcion de elminnar la analita de los posts, devuelve False para deshabilitar"""
        return False
    
    def has_add_permission(self, request, Obj=None):
        """Funcion que permite deshabilitar la opccion de agregar una nueva analitica, devuelve False para deshabilitar"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Funcion que permite deshabilitar la opcion de cambiar las analiticas, devuelve False para deshabilitar"""
        return False
        
    def post_title(self, obj):
        return obj.post.title
    
    post_title.short_description = 'Post Title'