# -*- coding: utf-8 -*-
# django stuff
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
# local stuff
from blog.forms import CommentForm
from blog.utils import ALLOWED_TAGS
from blog.models import Post, Comment

def blog(request, template_name='blog/blog.html'):
    
    # # Try to redirect old `QUERY_STRING` DotClear URLs
    # if request.method == "GET":
    #     get = request.GET.keys()
    #     if get and 'post' in get[0]:
    #         url = get[0].replace('post/', '')
    #         try:
    #             p = Post.objects.get( url=url )
    #             url_redirect = reverse('blog_detail', args=[
    #                 p.date_created.strftime('%Y'),
    #                 p.date_created.strftime('%m'),
    #                 p.date_created.strftime('%d'),
    #                 p.slug
    #             ])
    #             return HttpResponsePermanentRedirect( url_redirect )
    #         except Post.DoesNotExist:
    #             pass
    
    data = {
        'latest_posts': Post.public_objects.all()[:5],
        'selected': Post.public_objects.get_selected(num=10),
    }
    return render_to_response(template_name, data, RequestContext(request, {}))


def archives(request, template_name='blog/archives.html'):
    
    data = {
        'archives': Post.public_objects.only('date_created','title','slug').all(),
        'selected': Post.public_objects.get_selected(),
    }
    return render_to_response(template_name, data, RequestContext(request, {}))


def detail(request, year=None, month=None, day=None, slug=None, form_class=CommentForm, template_name='blog/detail.html'):
    
    post = get_object_or_404(
        Post,
        date_created__year=year,
        date_created__month=month,
        date_created__day=day,
        slug=slug,
        is_online=1,
    )
    
    preview = None
    form = form_class()
    
    try:
        prev = post.get_previous_by_date_created( is_online=1 )
    except Post.DoesNotExist:
        prev = None
    
    try:
        next = post.get_next_by_date_created( is_online=1 )
    except Post.DoesNotExist:
        next = None
    
    if request.method == "POST":
        
        if post.comments_are_closed():
            raise Http404
        
        ip = request.META.get('REMOTE_ADDR', '')
        form = form_class(request.POST, post=post, ip=ip)
        
        if form.is_valid():
            
            # simple anti spam http://www.fredboucher.com/posts/view/un-captcha-infaillible-
            if request.POST.get('email_confirm'):
                return HttpResponseRedirect( '/' )
            
            elif request.POST.get('preview'):
                preview = form.preview()
            
            elif request.POST.get('submit'):
                comment = form.save()
                url_redirect = reverse( 'blog_detail', args=[ year, month, day, slug, ] )
                # pass a get parameter `pub=1` and a fragment identifier `#c234` to display a confirmation msg
                return HttpResponseRedirect( '%s?pub=1#c%s' % ( url_redirect, comment.pk ) )
    
    data = {
        'here': 'blog',
        'p': post,
        'comments': post.comments.filter( is_online=1 ),
        'allowed_tags': ALLOWED_TAGS,
        'form': form,
        'prev': prev,
        'next': next,
        'preview': preview,
        'pub': request.GET.get('pub', None),
    }
    return render_to_response(template_name, data, RequestContext(request, {}))


def search(request, template_name='blog/search.html'):
    
    results = None
    search_term = None
    
    if request.method == "GET":
        search_term = request.GET.get('q', None)
        if search_term:
            results = Post.public_objects.filter( words__icontains=search_term )
    
    data = {
        'results': results,
        'search_term': search_term,
    }
    return render_to_response(template_name, data, RequestContext(request, {}))

