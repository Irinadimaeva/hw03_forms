from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..views import POSTS_COUNT

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_ira = User.objects.create_user(username='ira')
        cls.author_ramiz = User.objects.create_user(username='ramiz')

        cls.group_cat = Group.objects.create(
            title='Кошечки',
            slug='cats',
            description='Тестовое описание',
        )

        cls.group_dog = Group.objects.create(
            title='Собачки',
            slug='dogs',
            description='Тестовое описание',
        )

        cls.post_pages_per_author = 2
        cls.posts_ira = []
        cls.post_group_cat = None
        for _ in range(POSTS_COUNT * cls.post_pages_per_author):
            post = Post.objects.create(
                author=cls.author_ira,
                text=f'Пост от {cls.author_ira.username}',
                group=cls.group_cat,
            )
            cls.post_group_cat = post.id
            cls.posts_ira.append(post)

        cls.posts_ramiz = []
        cls.post_group_dog = None
        for _ in range(POSTS_COUNT * cls.post_pages_per_author):
            post = Post.objects.create(
                author=cls.author_ramiz,
                text=f'Пост от {cls.author_ramiz.username}',
                group=cls.group_dog,
            )
            cls.post_group_dog = post.id
            cls.posts_ramiz.append(post)

    def setUp(self) -> None:
        self.guest_client = Client()

        self.ira_client = Client()
        self.ira_client.force_login(self.author_ira)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = [
            ['posts/index.html', reverse('posts:index')],
            [
                'posts/group_list.html',
                reverse(
                    'posts:group_list', kwargs={'slug': self.group_cat.slug}
                )
            ],
            ['posts/profile.html', reverse(
                'posts:profile', kwargs={'username': self.author_ira.username}
            )],
            [
                'posts/post_detail.html',
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.posts_ira[0].id}
                )
            ],
            ['posts/create_post.html',
             reverse(
                 'posts:post_edit',
                 kwargs={'post_id': self.posts_ira[0].id}
             )],
            ['posts/create_post.html', reverse('posts:post_create')],
        ]
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for element in templates_pages_names:
            template = element[0]
            reverse_name = element[1]
            with self.subTest(reverse_name=reverse_name):
                response = self.ira_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page(self):
        response = self.ira_client.get(reverse('posts:index'))
        self.check_context_paginator(
            page_obj=response.context['page_obj'],
            objects_count=POSTS_COUNT,
            total_objects_count=len(self.posts_ira) + len(self.posts_ramiz),
            check_object_id=self.post_group_dog,
            page_num=1,
        )

        response = self.ira_client.get(reverse('posts:index') + "?page=2")
        self.check_context_paginator(
            page_obj=response.context['page_obj'],
            objects_count=POSTS_COUNT,
            total_objects_count=len(self.posts_ira) + len(self.posts_ramiz),
            check_object_id=30,
            page_num=2,
        )

    def test_group_list_page(self):
        url = reverse('posts:group_list', kwargs={'slug': self.group_dog.slug})
        response = self.ira_client.get(url)
        self.check_context_paginator(
            page_obj=response.context['page_obj'],
            objects_count=POSTS_COUNT,
            total_objects_count=len(self.posts_ira),
            check_object_id=self.post_group_dog,
            page_num=1,
        )
        self.assertEqual(response.context['group'].id, self.group_dog.id)
        self.check_posts_group(
            response.context['page_obj'].object_list, self.group_dog.id
        )

        response = self.ira_client.get(url + "?page=2")
        self.check_context_paginator(
            page_obj=response.context['page_obj'],
            objects_count=POSTS_COUNT,
            total_objects_count=len(self.posts_ira),
            check_object_id=25,
            page_num=2,
        )
        self.check_posts_group(
            response.context['page_obj'].object_list, self.group_dog.id
        )

    def check_posts_group(self, posts, expected_group_id):
        for obj in posts:
            self.assertIsNotNone(obj.group)
            self.assertEqual(obj.group.id, expected_group_id)

    def test_profile_page(self):
        url = reverse(
            'posts:profile',
            kwargs={'username': self.author_ramiz.username}
        )
        response = self.ira_client.get(url)

        self.check_context_paginator(
            page_obj=response.context['page_obj'],
            objects_count=POSTS_COUNT,
            total_objects_count=len(self.posts_ramiz),
            check_object_id=self.post_group_dog,
            page_num=1,
        )
        self.assertEqual(
            response.context['author'].username,
            self.author_ramiz.username
        )

        response = self.ira_client.get(url + "?page=2")
        self.check_context_paginator(
            page_obj=response.context['page_obj'],
            objects_count=POSTS_COUNT,
            total_objects_count=len(self.posts_ramiz),
            check_object_id=25,
            page_num=2,
        )

    def test_post_detail(self):
        url = reverse(
            'posts:post_detail', kwargs={'post_id': self.posts_ramiz[0].id}
        )
        response = self.ira_client.get(url)
        self.assertEqual(
            response.context['post'].id,
            self.posts_ramiz[0].id
        )

    def test_post_edit(self):
        url = reverse(
            'posts:post_edit', kwargs={'post_id': self.posts_ira[0].id}
        )
        response = self.ira_client.get(url)
        self.assertEqual(response.context['is_edit'], True)

        expected_form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        self.check_form_fields(
            actual_form_fields=response.context['form'],
            expected_form_fields=expected_form_fields,
        )

    def test_post_create(self):
        url = reverse('posts:post_create')
        response = self.ira_client.get(url)
        self.assertEqual(response.context['is_edit'], False)

        expected_form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        self.check_form_fields(
            actual_form_fields=response.context['form'],
            expected_form_fields=expected_form_fields,
        )

    def check_form_fields(self, actual_form_fields, expected_form_fields):
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in expected_form_fields.items():
            with self.subTest(value=value):
                form_field = actual_form_fields.fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def check_context_paginator(
            self,
            page_obj,
            objects_count,
            total_objects_count,
            page_num,
            check_object_id,
    ):
        self.assertEqual(page_obj.number, page_num)
        self.assertEqual(len(page_obj), objects_count)
        self.assertEqual(page_obj.paginator.count, total_objects_count)
        object_found = False
        for obj in page_obj.object_list:
            if check_object_id == obj.id:
                object_found = True
                break

        self.assertTrue(
            object_found,
            f'Object with id {check_object_id} has not been found'
        )
