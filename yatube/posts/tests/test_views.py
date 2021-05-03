from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа',
            slug='test-slug'
        )
        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug='another-test-slug'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Petuh')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Text',
            author=self.user,
            group=self.group
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'new_post.html': reverse('posts:new_post'),
            'group.html': reverse('posts:group', kwargs={'slug': 'test-slug'}),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page'][0].text, 'Text')
        self.assertEqual(response.context['page'][0].author, self.user)
        self.assertEqual(response.context['page'][0].group, self.group)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group', kwargs={'slug': 'test-slug'}))
        self.assertEqual(response.context['group'].title, 'Группа')
        self.assertEqual(response.context['page'][0].text, 'Text')
        self.assertEqual(response.context['page'][0].author, self.user)
        self.assertEqual(response.context['page'][0].group, self.group)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_group_pages_not_show_new_post(self):
        """Новый пост не попал в неправильную группу"""
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'another-test-slug'}))
        self.assertTrue(self.post not in response.context['page'])

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['page'][0], self.post)
        self.assertEqual(response.context['author'], self.user)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('posts:post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['author'], self.user)

    def test_about_author_page_for_guest(self):
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)

    def test_about_tech_page_for_guest(self):
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="user")
        cls.group = Group.objects.create(
            title="Название группы",
            slug="test-slug",
            description="тестовый текст"
        )
        for i in range(13):
            Post.objects.create(
                text=f"Тестовый текст {i}",
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()

    def test_index_first_page_contains_ten_records(self):
        """Передаётся 10 записей на странице"""
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_paginator_second_page(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
