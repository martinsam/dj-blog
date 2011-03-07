# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from blog.models import Post, Comment

class BlogFeed(Feed):
    feed_type = Atom1Feed

class AtomEntryFeed(Feed):
    title = "Blog"
    link = "/blog/"
    description = "Describe your blog"
    description_template = "blog/feeds/post_desc.html"
    
    def items(self):
        return Post.objects.filter(is_online=1).order_by('-date_created')[:10]
    
    def item_description(self, item):
        return item.content
    
    def item_link(self, item):
        return item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.date_created

class AtomCommentFeed(Feed):
    title = "Blog - Comments"
    link = ""
    description = ""
    description_template = "blog/feeds/comment_desc.html"
    
    def items(self):
        return Comment.objects.filter(is_online=1).order_by('-date_created')[:10]
    
    def item_description(self, item):
        return item.comment
    
    def item_link(self, item):
        return item.post.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.date_created

