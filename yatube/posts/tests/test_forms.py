from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.urls import reverse

User = get_user_model()


class CreatePostFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Petuh')
        self.user.save()
        self.client = Client()
        self.client.force_login(self.user)
        self.form_data = {
            'text': 'Белиберда бла бла',
            'author': self.user,
        }
        self.group = Group.objects.create(
            title='Заголовок',
            slug='test-1',
            description='Описание'
        )
        self.post = Post.objects.create(
            text='Белиберда бла бла',
            author=self.user,
        )
        self.post_count = Post.objects.count()

    def testing_creating_post(self):
        post_count = Post.objects.count()
        response = self.client.post(
            reverse('posts:new_post'),
            data=self.form_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, reverse('posts:index'))

    def test_post_edit_create_post_end_redirect(self):
        """Тест post_edit"""
        post_count = self.post_count
        text = 'Белиберда бла бла'
        response_index = self.client.post(
            reverse('posts:index')
        )
        post = response_index.context.get('page')[0]
        self.assertEqual(post.text, text)
        self.assertEqual(Post.objects.count(), post_count)
