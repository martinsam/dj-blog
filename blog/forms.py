# -*- coding: utf-8 -*-
# django stuff
from django.db import models
from django.utils.translation import activate, ugettext_lazy as _
from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.forms.util import ValidationError
# email stuff
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
# local stuff
from blog.utils import wordify, strip_tags, sanitize_html, ALLOWED_TAGS
from blog.models import Comment

BLOG_NOTIFY_NEW_COMMENT = False
BLOG_NEW_COMMENT_SENDER = 'Sender <mail@domain.com>'
BLOG_NEW_COMMENT_TO = 'mail@domain.com'

class CommentForm(forms.ModelForm):
    """
    Post a comment
    """
    
    def __init__(self, *args, **kwargs):
        self.post = kwargs.pop('post', None)
        self.ip = kwargs.pop('ip', None)
        super(CommentForm, self).__init__(*args, **kwargs)
    
    def clean_author(self):
        author = self.cleaned_data['author'].strip()
        if not author:
            raise forms.ValidationError(_(u"Ce champ est obligatoire."))
        return author
    
    def clean_comment(self):
        comment = self.cleaned_data['comment'].strip()
        if not comment:
            raise forms.ValidationError(_(u"Ce champ est obligatoire."))
        return comment
    
    def preview(self):
        comment = super(CommentForm, self).save(commit=False)
        comment.post = self.post
        comment.ip = self.ip
        comment.words = wordify( comment.comment )
        comment.comment = sanitize_html( comment.comment )
        return comment
    
    def save(self, force_insert=False, force_update=False, commit=True):
        
        comment = super(CommentForm, self).save(commit=False)
        
        comment.post = self.post
        comment.ip = self.ip
        comment.words = wordify( comment.comment )
        comment.comment = sanitize_html( comment.comment )
        
        # check for duplicate comment
        try:
            comment = Comment.objects.get(
                author=comment.author,
                post=comment.post,
                words=comment.words,
                comment=comment.comment,
            )
            # return old comment silently
            return comment
        except Comment.DoesNotExist:
            pass
        
        comment.save()
        
        if BLOG_NOTIFY_NEW_COMMENT:
            context = {
                "comment": strip_tags(comment.comment),
                "author": comment.author,
                "url": comment.post.get_absolute_url(),
                "current_site": Site.objects.get_current(),
            }
            subject = render_to_string('blog/emails/new_comment_subject.txt', context)
            message = render_to_string('blog/emails/new_comment_body.txt', context)
            sender = BLOG_NEW_COMMENT_SENDER
            to = BLOG_NEW_COMMENT_TO
            email = EmailMessage( subject, message, sender, [to] )
            email.send()
        
        return comment
    
    class Meta:
        model = Comment
        fields = ('author', 'email', 'site', 'comment')

