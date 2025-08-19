from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Category, Post, Heading

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'parent', 'slug',)
    search_fields = ('name', 'title', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)
    ordering = ('name',)
    readonly_fields = ('id',)


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