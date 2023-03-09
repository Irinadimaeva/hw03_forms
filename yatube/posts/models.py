from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Название', max_length=200)
    slug = models.SlugField(
        verbose_name='URL группы', max_length=200, unique=True
    )
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Группа постов'
        verbose_name_plural = 'Группы постов'

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    DESCRIPTION_TEMPLATE = ('Автор: {author}; '
                            'Пост: {text}; '
                            'Дата: {pub_date}')

    text = models.TextField(
        verbose_name='Текст поста', help_text='Текст нового поста', )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts',
        verbose_name='Автор поста', )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, related_name='posts', blank=True,
        null=True, verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост', )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        # выводим текст поста
        return self.DESCRIPTION_TEMPLATE.format(
            author=self.author.get_full_name(),
            text=self.text[:15],
            pub_date=self.pub_date.strftime('%d.%m.%Y')
        )
