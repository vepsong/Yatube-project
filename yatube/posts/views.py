from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

POSTS_NUM = 10


def paginator(queryset, request):
    """Универсальная функция-паджинатор."""
    paginator = Paginator(queryset, POSTS_NUM)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Фунция вызова главной страницы."""
    get_posts = Post.objects.all()
    context = {
        'page_obj': paginator(get_posts, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Функция вызова сгруппированной по постам страницы."""
    group = get_object_or_404(Group, slug=slug)
    get_posts = group.posts.all().order_by('-pub_date')
    context = {
        'group': group,
        'page_obj': paginator(get_posts, request),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Функция вызова персональной страницы пользователя."""
    author = get_object_or_404(User, username=username)
    get_posts = author.posts.all().order_by('-pub_date')

    if request.user.is_authenticated:
        context = {
            'author': author,
            'page_obj': paginator(get_posts, request),
            'follower': Follow.objects.filter(
                user=request.user,
                author=author,
            ),
            'following': Follow.objects.filter(
                user=request.user,
                author=author,
            ),
        }
    else:
        context = {
            'author': author,
            'page_obj': paginator(get_posts, request),
        }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Функция вызова страницы с подробной информации о публикации."""
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': paginator(comments, request),
        'is_comment': True
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Функция вызова страницы для создания публикации."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Функция вызова страницы для редактирования публикации."""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    is_edit = True

    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post.pk)
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'is_edit': is_edit, 'post': post})
    else:
        return redirect('posts:post_detail', post.pk)


@login_required
def add_comment(request, post_id):
    """Функция вызова страницы для создания комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(
        request,
        'posts/post_detail.html',
        {'form': form, 'post': post}
    )


@login_required
def follow_index(request):
    """Функция вызова вкладки follow на стр. posts:main_page."""
    get_posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': paginator(get_posts, request),
    }
    return render(
        request,
        'posts/follow.html',
        context,
    )


@login_required
def profile_follow(request, username):
    """Функция подписки на автора."""
    author = get_object_or_404(User, username=username)
    redirect_address = redirect('posts:profile', username=username)

    if author == request.user:
        return redirect_address
    follower = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()

    if follower is True:
        return redirect_address
    Follow.objects.create(user=request.user, author=author)
    return redirect_address


@login_required
def profile_unfollow(request, username):
    """Функция отписки от автора."""
    author = get_object_or_404(User, username=username)
    redirect_address = redirect('posts:profile', username=username)
    if author == request.user:
        return redirect(redirect_address)

    following = get_object_or_404(Follow, user=request.user, author=author)
    following.delete()
    return redirect_address
