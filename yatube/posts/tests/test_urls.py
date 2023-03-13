from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
        )

    def setUp(self) -> None:
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # авторизированный
        self.user = User.objects.create_user(username='authorized_client')
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_open_pages(self):
        """ Тестирование страниц доступных любому пользователю."""
        context = [
            '/',
            f'/group/{self.group.slug}/',
            '/profile/auth/',
            f'/posts/{self.post.id}/',
        ]
        for address in context:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_close_pages(self):
        """ Тестирование страниц доступных авторизованному пользователю."""
        context = [
            '/create/',
        ]
        for address in context:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_author_pages(self):
        """Тестирование страниц доступных автору."""
        context = [
            f'/posts/{self.post.id}/edit/',
        ]
        for address in context:
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_unexist_page_url(self):
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(
            response.status_code,
            404,
            'Тест на Проверку страницы несуществующей'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)


