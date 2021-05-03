from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from .models import Group, Post
from .forms import PostForm

User = get_user_model()


def index(request):
    latest = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all().order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, "new_post.html", {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:index')


def profile(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    posts = author.posts.all().order_by('-pub_date')
    count_posts = posts.count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'user': user,
        'author': author,
        'page': page,
        'count_posts': count_posts,
    })


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    count_posts = author.posts.count()
    return render(request, 'post.html', {
        'author': author,
        'count_posts': count_posts,
        'post': post,
        'username': author.username
    })


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    if request.user != author:
        return redirect('posts:post', username=author.username,
                        post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post',
                            username=request.user.username,
                            post_id=post_id)
    return render(request, 'new_post.html',
                  {'form': form, 'author': author, 'post': post})
