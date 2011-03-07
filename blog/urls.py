# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from blog.feeds import AtomEntryFeed, AtomCommentFeed

feeds = {
    'posts': AtomEntryFeed,
    'comments': AtomCommentFeed,
}

urlpatterns = patterns('',
    url(r'^$', 'blog.views.blog', name='blog'),
    url(r'^archives', 'blog.views.archives', name='blog_archives'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>.*)$', 'blog.views.detail', name='blog_detail'),
    url(r'^search', 'blog.views.search', name='blog_search'),
    
    # RSS Feeds
    url(r'^feed/atom/posts$', AtomEntryFeed(), name='blog_entries_feed'),
    url(r'^feed/atom/comments$', AtomCommentFeed(), name='blog_comments_feed'),
)

