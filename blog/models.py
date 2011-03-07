# -*- coding: utf-8 -*-
import os
import codecs
from datetime import datetime, timedelta
# django stuff
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.template.defaultfilters import slugify
# local stuff
from blog.utils import wordify


# python manage.py dumpdata blog --format=xml --indent=4 > ~/Desktop/blog.xml

class PostManager(models.Manager):
    
    def get_query_set(self):
        return super(PostManager, self).get_query_set().filter(is_online=True)
    
    def get_selected(self,num=None):
        if num is None:
            return self.filter(is_selected=1).order_by('-pk')
        return self.filter(is_selected=1).order_by('-pk')[:num]

class Post(models.Model):
    
    AUTHOR_CHOICES = (
        ('author', u'Author'),
    )
    
    DAYS_BEFORE_CLOSING_COMMENTS = 31
    
    author = models.CharField(_('Auteur'), max_length=50, choices=AUTHOR_CHOICES)
    date_created = models.DateTimeField(_(u'Date de création'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Date de modification'), auto_now=True)
    # on conserve `url` pour corriger d'éventuels pb compatibilité url/slug (migration DotClear)
    url = models.CharField(_('URL'), max_length=255, null=True, blank=True)
    title = models.CharField(_('Titre'), max_length=255)
    content = models.TextField(_('Billet'))
    words = models.TextField(_('Mots'), null=True, blank=True)
    is_online = models.BooleanField(_('Online'), default=True)
    is_selected = models.BooleanField(_(u'Sélectionné'), default=False)
    num_comment = models.IntegerField(_('Nombre de commentaires'), null=True, blank=True, default=0)
    slug = models.SlugField(_('Slug'), max_length=255, null=True, blank=True)
    
    objects = models.Manager()
    public_objects = PostManager()
    
    @models.permalink
    def get_absolute_url(self):
        return ('blog_detail', (), {
            'year': self.date_created.strftime('%Y'),
            'month': self.date_created.strftime('%m'),
            'day': self.date_created.strftime('%d'),
            'slug': self.slug,
        })
    
    def __unicode__(self):
        return self.title
    
    def is_old(self):
        time_elapsed_since_publication = datetime.now() - self.date_created
        if time_elapsed_since_publication.days > 365:
            return True
        else:
            return False
    
    def comments_are_closed(self):
        time_elapsed_since_publication = datetime.now() - self.date_created
        if time_elapsed_since_publication.days > self.DAYS_BEFORE_CLOSING_COMMENTS:
            return True
        else:
            return False
    
    def get_comments_closing_date(self):
        closing_date = self.date_created + timedelta(days=self.DAYS_BEFORE_CLOSING_COMMENTS)
        return closing_date
    
    def get_comments_time_before_closing(self):
        if not self.comments_are_closed():
            comments_closing_date = self.get_comments_closing_date()
            timedelta_before_closing = comments_closing_date - datetime.now()
            time_hash = {
                'days':    timedelta_before_closing.days if timedelta_before_closing.days >= 0 else 0,
                'hours':   timedelta_before_closing.seconds // 3600,
                'minutes': (timedelta_before_closing.seconds % 3600) // 60,
                'seconds': timedelta_before_closing.seconds % 60,
            }
            return time_hash
        return False
    
    def save(self, *args, **kwargs):
        self.words = '%s %s' % (wordify(self.title), wordify(self.content))
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save()
    
    class Meta:
        db_table = 'blog_post'
        ordering = ['-date_created']
        verbose_name = _(u'Post')
        verbose_name_plural = _(u'Posts')


class CommentManager(models.Manager):
    
    def get_query_set(self):
        return super(CommentManager, self).get_query_set().filter(is_online=True)

class Comment(models.Model):
    
    post = models.ForeignKey(Post, related_name='comments')
    date_created = models.DateTimeField(_(u'Date de création'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Date de modification'), auto_now=True)
    author = models.CharField(_('Nom'), max_length=255)
    email = models.EmailField(_('Email'), null=True, blank=True)
    site = models.URLField(_('Site'), verify_exists=False, null=True, blank=True)
    comment = models.TextField(_('Commentaire'))
    words = models.TextField(_('Mots'), null=True, blank=True)
    ip = models.IPAddressField(_('IP'), null=True, blank=True)
    is_online = models.BooleanField(_('Online'), default=True)
    
    objects = models.Manager()
    public_objects = CommentManager()
    
    def __unicode__(self):
        return self.author
    
    def save(self, *args, **kwargs):
        self.words = wordify(self.comment)
        super(Comment, self).save()
    
    class Meta:
        db_table = 'blog_comment'
        ordering = ['date_created']
        verbose_name = _('Commentaire')
        verbose_name_plural = _('Commentaires')


# Signals

def generate_json_index(sender, instance=None, **kwargs):
    """
    Generate posts JSON index
    touch blog_suggest.js
    sudo chmod 774 blog_suggest.js
    sudo chgrp www-data blog_suggest.js
    """
    all_posts = Post.objects.only('date_created','title','slug').filter(is_online=True).order_by('-pk')
    data = [
        {
            'title': post.title,
            'year': post.date_created.strftime('%Y'),
            'url': post.get_absolute_url(),
        }
        for post in all_posts
    ]
    output_file = os.path.join(settings.MEDIA_ROOT, 'json/blog_suggest.js')
    output = codecs.open(output_file, encoding='utf-8', mode='w')
    simplejson.dump(data, output, indent=None)
    output.close()
    return

# Uncomment to use a json_index
# post_save.connect(generate_json_index, sender=Post)

def set_num_comment(sender, instance=None, **kwargs):
    if instance is not None:
        post = instance.post
        post.num_comment = post.comments.filter( is_online=1 ).count()
        post.save()

post_save.connect(set_num_comment, sender=Comment)
post_delete.connect(set_num_comment, sender=Comment)

