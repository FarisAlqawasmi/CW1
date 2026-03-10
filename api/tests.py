import json
from django.test import TestCase, Client

from .models import Task, Habit


class RootRoutesTests(TestCase):
    """Tests for root and API root routes."""

    def setUp(self):
        self.client = Client()

    def test_get_root(self):
        """GET / returns API running message."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body.get('message'), 'Productivity Tracker API is running')

    def test_get_api_root(self):
        """GET /api/ returns welcome message and available endpoints."""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body.get('message'), 'Welcome to the Productivity Tracker API')
        self.assertIn('available_endpoints', body)
        self.assertEqual(body['available_endpoints'], ['/api/tasks/', '/api/habits/'])


class TaskAPITests(TestCase):
    """Tests for Task list, create, retrieve, update, delete."""

    def setUp(self):
        self.client = Client()
        self.list_url = '/api/tasks/'

    def test_create_task(self):
        """POST /api/tasks/ creates a task and returns 201 with the task."""
        data = {'title': 'Finish report', 'description': 'Write the summary'}
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body['title'], 'Finish report')
        self.assertEqual(body['description'], 'Write the summary')
        self.assertIn('id', body)
        self.assertIn('created_at', body)
        self.assertEqual(Task.objects.count(), 1)

    def test_retrieve_task_list(self):
        """GET /api/tasks/ returns list of tasks."""
        Task.objects.create(title='Task A')
        Task.objects.create(title='Task B')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 2)
        titles = [t['title'] for t in body]
        self.assertIn('Task A', titles)
        self.assertIn('Task B', titles)

    def test_retrieve_one_task(self):
        """GET /api/tasks/{id}/ returns a single task."""
        task = Task.objects.create(title='Single task', priority='high')
        url = f'/api/tasks/{task.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['id'], task.id)
        self.assertEqual(body['title'], 'Single task')
        self.assertEqual(body['priority'], 'high')

    def test_update_task(self):
        """PUT /api/tasks/{id}/ updates a task and returns 200."""
        task = Task.objects.create(title='Old title', status='not_started')
        url = f'/api/tasks/{task.id}/'
        data = {'title': 'New title', 'status': 'in_progress'}
        response = self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['title'], 'New title')
        self.assertEqual(body['status'], 'in_progress')
        task.refresh_from_db()
        self.assertEqual(task.title, 'New title')
        self.assertEqual(task.status, 'in_progress')

    def test_delete_task(self):
        """DELETE /api/tasks/{id}/ removes the task and returns 204."""
        task = Task.objects.create(title='To delete')
        url = f'/api/tasks/{task.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(pk=task.id).exists())

    def test_task_not_found_returns_404(self):
        """GET /api/tasks/{id}/ for non-existent task returns 404."""
        response = self.client.get('/api/tasks/99999/')
        self.assertEqual(response.status_code, 404)

    def test_create_task_invalid_json_returns_400(self):
        """POST /api/tasks/ with invalid JSON body returns 400."""
        response = self.client.post(
            self.list_url,
            data='not valid json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn('error', body)

    def test_create_task_validation_error_returns_400(self):
        """POST /api/tasks/ with missing title returns 400."""
        response = self.client.post(
            self.list_url,
            data=json.dumps({'description': 'No title'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn('errors', body)

    def test_task_list_wrong_method_returns_405(self):
        """PUT /api/tasks/ returns 405 (only GET, POST allowed)."""
        response = self.client.put(
            self.list_url,
            data=json.dumps({'title': 'Task'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 405)

    def test_task_detail_wrong_method_returns_405(self):
        """POST /api/tasks/{id}/ returns 405 (only GET, PUT, DELETE allowed)."""
        task = Task.objects.create(title='Task')
        response = self.client.post(
            f'/api/tasks/{task.id}/',
            data=json.dumps({'title': 'Updated'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 405)

    def test_task_list_filter_by_status(self):
        """GET /api/tasks/?status=completed returns only completed tasks."""
        Task.objects.create(title='Not done', status='not_started')
        Task.objects.create(title='Done one', status='completed')
        Task.objects.create(title='Done two', status='completed')
        response = self.client.get(self.list_url + '?status=completed')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        for task in body:
            self.assertEqual(task['status'], 'completed')

    def test_task_list_filter_by_priority(self):
        """GET /api/tasks/?priority=high returns only high-priority tasks."""
        Task.objects.create(title='Low task', priority='low')
        Task.objects.create(title='High one', priority='high')
        Task.objects.create(title='High two', priority='high')
        response = self.client.get(self.list_url + '?priority=high')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        for task in body:
            self.assertEqual(task['priority'], 'high')

    def test_task_list_filter_by_status_and_priority(self):
        """GET /api/tasks/?status=in_progress&priority=medium returns matching tasks."""
        Task.objects.create(title='Other', status='completed', priority='medium')
        Task.objects.create(title='Match one', status='in_progress', priority='medium')
        Task.objects.create(title='Match two', status='in_progress', priority='medium')
        Task.objects.create(title='Wrong status', status='not_started', priority='medium')
        Task.objects.create(title='Wrong priority', status='in_progress', priority='high')
        response = self.client.get(self.list_url + '?status=in_progress&priority=medium')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        for task in body:
            self.assertEqual(task['status'], 'in_progress')
            self.assertEqual(task['priority'], 'medium')

    def test_task_list_invalid_status_returns_400(self):
        """GET /api/tasks/?status=pending returns 400."""
        response = self.client.get(self.list_url + '?status=pending')
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn('errors', body)

    def test_task_list_invalid_priority_returns_400(self):
        """GET /api/tasks/?priority=urgent returns 400."""
        response = self.client.get(self.list_url + '?priority=urgent')
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn('errors', body)


class HabitAPITests(TestCase):
    """Tests for Habit list, create, retrieve, update, delete."""

    def setUp(self):
        self.client = Client()
        self.list_url = '/api/habits/'

    def test_create_habit(self):
        """POST /api/habits/ creates a habit and returns 201 with the habit."""
        data = {'name': 'Morning run', 'frequency': 'daily', 'streak': 0}
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body['name'], 'Morning run')
        self.assertEqual(body['frequency'], 'daily')
        self.assertEqual(body['streak'], 0)
        self.assertIn('id', body)
        self.assertIn('created_at', body)
        self.assertEqual(Habit.objects.count(), 1)

    def test_retrieve_habit_list(self):
        """GET /api/habits/ returns list of habits."""
        Habit.objects.create(name='Habit A')
        Habit.objects.create(name='Habit B')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 2)
        names = [h['name'] for h in body]
        self.assertIn('Habit A', names)
        self.assertIn('Habit B', names)

    def test_retrieve_one_habit(self):
        """GET /api/habits/{id}/ returns a single habit."""
        habit = Habit.objects.create(name='Single habit', frequency='weekly', streak=2)
        url = f'/api/habits/{habit.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['id'], habit.id)
        self.assertEqual(body['name'], 'Single habit')
        self.assertEqual(body['frequency'], 'weekly')
        self.assertEqual(body['streak'], 2)

    def test_update_habit(self):
        """PUT /api/habits/{id}/ updates a habit and returns 200."""
        habit = Habit.objects.create(name='Old habit', streak=3)
        url = f'/api/habits/{habit.id}/'
        data = {'name': 'Updated habit', 'streak': 5, 'completed_today': True}
        response = self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['name'], 'Updated habit')
        self.assertEqual(body['streak'], 5)
        self.assertTrue(body['completed_today'])
        habit.refresh_from_db()
        self.assertEqual(habit.name, 'Updated habit')
        self.assertEqual(habit.streak, 5)
        self.assertTrue(habit.completed_today)

    def test_delete_habit(self):
        """DELETE /api/habits/{id}/ removes the habit and returns 204."""
        habit = Habit.objects.create(name='To delete')
        url = f'/api/habits/{habit.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Habit.objects.filter(pk=habit.id).exists())

    def test_habit_not_found_returns_404(self):
        """GET /api/habits/{id}/ for non-existent habit returns 404."""
        response = self.client.get('/api/habits/99999/')
        self.assertEqual(response.status_code, 404)

    def test_create_habit_invalid_json_returns_400(self):
        """POST /api/habits/ with invalid JSON body returns 400."""
        response = self.client.post(
            self.list_url,
            data='not valid json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn('error', body)

    def test_create_habit_validation_error_returns_400(self):
        """POST /api/habits/ with missing name returns 400."""
        response = self.client.post(
            self.list_url,
            data=json.dumps({'frequency': 'daily'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn('errors', body)

    def test_habit_list_wrong_method_returns_405(self):
        """PUT /api/habits/ returns 405 (only GET, POST allowed)."""
        response = self.client.put(
            self.list_url,
            data=json.dumps({'name': 'Habit'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 405)

    def test_habit_detail_wrong_method_returns_405(self):
        """POST /api/habits/{id}/ returns 405 (only GET, PUT, DELETE allowed)."""
        habit = Habit.objects.create(name='Habit')
        response = self.client.post(
            f'/api/habits/{habit.id}/',
            data=json.dumps({'name': 'Updated'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 405)

    def test_habit_list_filter_by_frequency(self):
        """GET /api/habits/?frequency=daily returns only daily habits."""
        Habit.objects.create(name='Weekly one', frequency='weekly')
        Habit.objects.create(name='Daily one', frequency='daily')
        Habit.objects.create(name='Daily two', frequency='daily')
        response = self.client.get(self.list_url + '?frequency=daily')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        for habit in body:
            self.assertEqual(habit['frequency'], 'daily')

    def test_habit_list_filter_by_completed_today_true(self):
        """GET /api/habits/?completed_today=true returns only habits completed today."""
        Habit.objects.create(name='Not done', completed_today=False)
        Habit.objects.create(name='Done one', completed_today=True)
        Habit.objects.create(name='Done two', completed_today=True)
        response = self.client.get(self.list_url + '?completed_today=true')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        for habit in body:
            self.assertTrue(habit['completed_today'])

    def test_habit_list_filter_by_completed_today_false(self):
        """GET /api/habits/?completed_today=false returns only habits not completed today."""
        Habit.objects.create(name='Done', completed_today=True)
        Habit.objects.create(name='Not done one', completed_today=False)
        Habit.objects.create(name='Not done two', completed_today=False)
        response = self.client.get(self.list_url + '?completed_today=false')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        for habit in body:
            self.assertFalse(habit['completed_today'])

    def test_habit_list_filter_by_frequency_and_completed_today(self):
        """GET /api/habits/?frequency=weekly&completed_today=false returns matching habits."""
        Habit.objects.create(name='Other', frequency='daily', completed_today=False)
        Habit.objects.create(name='Match one', frequency='weekly', completed_today=False)
        Habit.objects.create(name='Match two', frequency='weekly', completed_today=False)
        Habit.objects.create(name='Wrong frequency', frequency='daily', completed_today=False)
        Habit.objects.create(name='Wrong completed', frequency='weekly', completed_today=True)
        response = self.client.get(self.list_url + '?frequency=weekly&completed_today=false')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        for habit in body:
            self.assertEqual(habit['frequency'], 'weekly')
            self.assertFalse(habit['completed_today'])

    def test_habit_list_invalid_frequency_returns_400(self):
        """GET /api/habits/?frequency=monthly returns 400."""
        response = self.client.get(self.list_url + '?frequency=monthly')
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn('errors', body)

    def test_habit_list_invalid_completed_today_returns_400(self):
        """GET /api/habits/?completed_today=yes returns 400."""
        response = self.client.get(self.list_url + '?completed_today=yes')
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn('errors', body)
