# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from blog.models import Post, Comment

# class CommentInline(admin.StackedInline):
#     model = Comment
#     exclude = ('words',)
#     extra = 0

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created', 'updated', 'is_online', 'num_comment')
    search_fields = ['title']
    list_per_page = 100
    list_filter = ['is_selected', 'is_online']
    ordering = ('-id',)
    list_display_links = ['id', 'title']
    exclude = ('words',)
    date_hierarchy = 'date_created'
    
    # inlines = [ CommentInline, ]
    
    def created(self, obj):
        return obj.date_created.strftime("%d/%m/%Y")
    created.short_description = _(u'Création')
    
    def updated(self, obj):
        return obj.date_updated.strftime("%d/%m/%Y")
    updated.short_description = _(u'Updaté')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_id', 'author', 'post', 'created', 'updated', 'is_online', 'ip')
    search_fields = ['comment', 'post__pk']
    list_per_page = 100
    list_filter = ['is_online']
    ordering = ('-id',)
    list_display_links = ['id', 'author']
    exclude = ('words',)
    date_hierarchy = 'date_created'
    
    def post_id(self, obj):
        return '%s' % obj.post.pk
    post_id.short_description = _(u'Commentaire')
    
    def created(self, obj):
        return obj.date_created.strftime("%d/%m/%Y")
    created.short_description = _(u'Création')
    
    def updated(self, obj):
        return obj.date_updated.strftime("%d/%m/%Y")
    updated.short_description = _(u'Updaté')

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)

