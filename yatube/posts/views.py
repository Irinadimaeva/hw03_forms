from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PostForm
from .models import Group, Post

POSTS_COUNT: int = 10

User = get_user_model()

"""
def only_user_view(request):
    if not request.user.is_authenticated:
        # Если пользователь не авторизован - отправляем его на страницу логина.
        return redirect('/auth/login/')
    # Если пользователь авторизован — здесь выполняется полезный код функции.
"""


def index(request):
    post_list = Post.objects.select_related('group')

    paginator = Paginator(post_list, POSTS_COUNT)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


# View-функция для страницы сообщества:
def group_posts(request, slug):
    template = 'posts/group_list.html'
    # Функция get_object_or_404 получает по заданным критериям объект
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # В нашем случае в переменную group будут переданы объекты модели Group,
    # поле slug у которых соответствует значению slug в запросе
    group = get_object_or_404(Group, slug=slug)

    posts = (
        group.posts.all()
    )

    paginator = Paginator(posts, POSTS_COUNT)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    # В словаре context отправляем информацию в шаблон
    context: dict = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = (
        user.posts.all()
    )

    paginator = Paginator(posts, POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context: dict = {
        'author': user,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # код запроса к модели и создание словаря контекста
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    # Создаём объект формы класса PostForm
    # и передаём в него полученные данные
    form = PostForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.instance.author = request.user
        # сохраняем объект в базу
        form.save()

        # Функция redirect перенаправляет пользователя
        # на другую страницу сайта, чтобы защититься
        # от повторного заполнения формы
        return redirect(
            reverse(
                'posts:profile',
                kwargs={'username': request.user.username}
            )
        )

    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post_id}
            )
        )

    form = PostForm(instance=post)

    if request.method == 'POST':
        # Создаём объект формы класса PostForm
        # и передаём в него полученные данные
        form = PostForm(request.POST, instance=post)

        # Если все данные формы валидны - работаем с "очищенными данными" формы
        if form.is_valid():
            # сохраняем объект в базу
            form.save()

            # Функция redirect перенаправляет пользователя
            # на другую страницу сайта, чтобы защититься
            # от повторного заполнения формы
            return redirect(
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': post_id}
                )
            )

    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': True}
    )
