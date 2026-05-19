from django.contrib import admin
from .models import Post,Comment

#admin site register here

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display=['title','slug','author_id','publish','status']
    list_filter=['status','created','publish']
    search_fields=['title','body']
    date_hierarchy='publish'
    prepopulated_fields={'slug':['title']}
    show_facets=admin.ShowFacets.ALWAYS

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']