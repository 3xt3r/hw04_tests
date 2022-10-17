from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User
from posts.forms import PostForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .utils import get_paginator


def index(request):
    post_context = get_paginator(Post.objects.all(), request)
    return render(request, 'posts/index.html', post_context)


def group_posts(request, slug):
    group = get_object_or_404(
        Group.objects.all().prefetch_related('posts'),
        slug=slug)
    context = {
        'group': group,
    }
    context.update(get_paginator(group.posts.all(), request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_count = author.posts.count()
    context = {
        'author': author,
        'posts_count': posts_count,
    }
    context.update(get_paginator(author.posts.all(), request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_info = get_object_or_404(Post, pk=post_id)
    posts_count = post_info.author.posts.count()
    context = {
        'post_info': post_info,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)

    if not form.is_valid():
        context = {'form': form}
        return render(request, 'posts/create_post.html', context)

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    username = request.user.username
    return redirect('posts:profile', username=username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.pk)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True, 'post_id': post_id, })
