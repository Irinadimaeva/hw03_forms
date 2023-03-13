from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    POST_TEXT = 'Тестовый пост'
    EMPTY_TEXT_ERROR = 'Обязательное поле.'
    UNKNOWN_GROUP_ERROR = (
        'Выберите корректный вариант. Вашего варианта нет среди '
        'допустимых значений.'
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='irina')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.ira_client = Client()
        self.ira_client.force_login(self.author)

    def test_create_post_empty_text(self):
        # Подсчитаем количество записей в Posts
        post_count = Post.objects.count()
        form_data = {
            'text': '',
        }

        response = self.ira_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Убедимся, что запись в базе данных не создалась:
        # сравним количество записей в Post до и после отправки формы
        self.assertEqual(Post.objects.count(), post_count)

        # Проверим, что форма вернула ошибку с ожидаемым текстом:
        # из объекта response берём словарь 'form',
        self.assertFormError(
            response,
            'form',
            'text',
            self.EMPTY_TEXT_ERROR
        )
        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, 200)

    def test_create_post_unknown_group(self):
        # Подсчитаем количество записей в Posts
        post_count = Post.objects.count()
        form_data = {
            'text': self.POST_TEXT,
            'group': 0
        }

        response = self.ira_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Убедимся, что запись в базе данных не создалась:
        # сравним количество записей в Post до и после отправки формы
        self.assertEqual(Post.objects.count(), post_count)

        # Проверим, что форма вернула ошибку с ожидаемым текстом:
        # из объекта response берём словарь 'form',
        self.assertFormError(
            response,
            'form',
            'group',
            self.UNKNOWN_GROUP_ERROR
        )
        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, 200)

    def test_create_post_success(self):
        # Подсчитаем количество записей в Posts
        post_count = Post.objects.count()

        form_data = {
            'text': self.POST_TEXT,
            'group': self.group.id,
        }

        response = self.ira_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            )
        )

        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)

        # Проверяем, что создалась запись
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text=self.POST_TEXT,
            ).exists()
        )

    def test_edit_post_empty_text(self):
        form_data = {
            'text': '',
        }

        response = self.ira_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )

        # Проверим, что форма вернула ошибку с ожидаемым текстом:
        # из объекта response берём словарь 'form',
        self.assertFormError(
            response,
            'form',
            'text',
            self.EMPTY_TEXT_ERROR
        )
        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, 200)

    def test_edit_post_unknown_group(self):
        form_data = {
            'text': self.POST_TEXT,
            'group': 0
        }

        response = self.ira_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )

        # Проверим, что форма вернула ошибку с ожидаемым текстом:
        # из объекта response берём словарь 'form',
        self.assertFormError(
            response,
            'form',
            'group',
            self.UNKNOWN_GROUP_ERROR
        )
        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, 200)

    def test_edit_post_success(self):
        form_data = {
            'text': self.POST_TEXT,
            'group': self.group.id,
        }

        response = self.ira_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )

        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )

        post = Post.objects.get(pk=self.post.id)

        self.assertEqual(post.group.id, self.group.id)
        self.assertEqual(post.text, self.POST_TEXT)
