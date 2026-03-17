from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Task


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')

    def test_task_creation(self):
        task = Task.objects.create(title='Test Task', owner=self.user)
        self.assertEqual(str(task), 'Test Task (owner: testuser)')
        self.assertFalse(task.completed)
        self.assertEqual(task.priority, 'medium')

    def test_task_fields(self):
        task = Task.objects.create(
            title='My Task', description='Some desc',
            completed=True, priority='high', owner=self.user
        )
        self.assertEqual(task.title, 'My Task')
        self.assertEqual(task.description, 'Some desc')
        self.assertTrue(task.completed)
        self.assertEqual(task.priority, 'high')


class TaskAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass1234')
        self.other_user = User.objects.create_user(username='bob', password='pass1234')
        self.admin = User.objects.create_superuser(username='admin', password='admin1234', email='admin@test.com')

        tokens = get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])

        self.task = Task.objects.create(title='Alice Task', description='desc', owner=self.user)

    def test_list_tasks_authenticated(self):
        url = reverse('task-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_tasks_unauthenticated(self):
        self.client.credentials()
        url = reverse('task-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task(self):
        url = reverse('task-list-create')
        data = {'title': 'New Task', 'description': 'Test desc', 'priority': 'high'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.filter(owner=self.user).count(), 2)

    def test_create_task_invalid_title(self):
        url = reverse('task-list-create')
        data = {'title': 'ab'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_task_detail(self):
        url = reverse('task-detail', kwargs={'pk': self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Alice Task')

    def test_update_task(self):
        url = reverse('task-detail', kwargs={'pk': self.task.pk})
        data = {'title': 'Updated Task', 'description': 'Updated', 'completed': True, 'priority': 'low'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)
        self.assertEqual(self.task.title, 'Updated Task')

    def test_partial_update_task(self):
        url = reverse('task-detail', kwargs={'pk': self.task.pk})
        response = self.client.patch(url, {'completed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_task(self):
        url = reverse('task-detail', kwargs={'pk': self.task.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.filter(owner=self.user).count(), 0)

    def test_other_user_cannot_delete(self):
        tokens = get_tokens_for_user(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
        url = reverse('task-detail', kwargs={'pk': self.task.pk})
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_filter_by_completed(self):
        Task.objects.create(title='Done Task', completed=True, owner=self.user)
        url = reverse('task-list-create') + '?completed=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_priority(self):
        Task.objects.create(title='High Task', priority='high', owner=self.user)
        url = reverse('task-list-create') + '?priority=high'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pagination(self):
        for i in range(15):
            Task.objects.create(title=f'Task {i}', owner=self.user)
        url = reverse('task-list-create') + '?page=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)


class UserAuthAPITest(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {'username': 'newuser', 'email': 'new@test.com', 'password': 'pass1234', 'password2': 'pass1234'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)

    def test_register_password_mismatch(self):
        url = reverse('register')
        data = {'username': 'newuser2', 'password': 'pass1234', 'password2': 'wrong'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        User.objects.create_user(username='loginuser', password='pass1234')
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': 'loginuser', 'password': 'pass1234'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_profile_authenticated(self):
        user = User.objects.create_user(username='profileuser', password='pass1234')
        tokens = get_tokens_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')
