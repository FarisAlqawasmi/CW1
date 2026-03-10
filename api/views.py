import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404

from .models import Task, Habit


# --- Root views ---

def root_view(request):
    """GET / → API running message."""
    return JsonResponse({'message': 'Productivity Tracker API is running'})


def api_root(request):
    """GET /api/ → API welcome and available endpoints."""
    return JsonResponse({
        'message': 'Welcome to the Productivity Tracker API',
        'available_endpoints': ['/api/tasks/', '/api/habits/'],
    })


# --- Helpers ---

def _serialize_task(task):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description or '',
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'priority': task.priority,
        'status': task.status,
        'created_at': task.created_at.isoformat(),
    }


def _serialize_habit(habit):
    return {
        'id': habit.id,
        'name': habit.name,
        'frequency': habit.frequency,
        'streak': habit.streak,
        'completed_today': habit.completed_today,
        'created_at': habit.created_at.isoformat(),
    }


def _parse_json(request):
    """Return (data_dict, None) or (None, JsonResponse with 400)."""
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return None, JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not isinstance(data, dict):
        return None, JsonResponse({'error': 'Expected a JSON object'}, status=400)
    return data, None


# --- Task choices for validation ---
TASK_PRIORITIES = {'low', 'medium', 'high'}
TASK_STATUSES = {'not_started', 'in_progress', 'completed'}


def _validate_task_data(data, for_update=False):
    """Return (attrs_dict, None) or (None, JsonResponse with 400)."""
    errors = []
    title = data.get('title')
    if not for_update and not title:
        errors.append('title is required')
    if title is not None and (not isinstance(title, str) or len(title.strip()) == 0):
        errors.append('title must be a non-empty string')
    if title is not None and len(title) > 255:
        errors.append('title must be at most 255 characters')

    description = data.get('description')
    if description is not None and not isinstance(description, str):
        errors.append('description must be a string')

    due_date = data.get('due_date')
    if due_date is not None and due_date != '':
        if not isinstance(due_date, str):
            errors.append('due_date must be a string (ISO date)')
        else:
            try:
                from datetime import datetime
                datetime.strptime(due_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                errors.append('due_date must be a valid ISO date (YYYY-MM-DD)')

    priority = data.get('priority')
    if priority is not None and priority not in TASK_PRIORITIES:
        errors.append('priority must be one of: low, medium, high')

    status = data.get('status')
    if status is not None and status not in TASK_STATUSES:
        errors.append('status must be one of: not_started, in_progress, completed')

    if errors:
        return None, JsonResponse({'errors': errors}, status=400)

    from datetime import date
    attrs = {}
    if title is not None:
        attrs['title'] = title.strip()
    if description is not None:
        attrs['description'] = description
    if 'due_date' in data:
        d = data['due_date']
        attrs['due_date'] = date.fromisoformat(d) if isinstance(d, str) and d.strip() else None
    if priority is not None:
        attrs['priority'] = priority
    if status is not None:
        attrs['status'] = status
    return attrs, None


# --- Habit choices for validation ---
HABIT_FREQUENCIES = {'daily', 'weekly'}


def _validate_habit_data(data, for_update=False):
    """Return (attrs_dict, None) or (None, JsonResponse with 400)."""
    errors = []
    name = data.get('name')
    if not for_update and not name:
        errors.append('name is required')
    if name is not None and (not isinstance(name, str) or len(name.strip()) == 0):
        errors.append('name must be a non-empty string')
    if name is not None and len(name) > 255:
        errors.append('name must be at most 255 characters')

    frequency = data.get('frequency')
    if frequency is not None and frequency not in HABIT_FREQUENCIES:
        errors.append('frequency must be one of: daily, weekly')

    streak = data.get('streak')
    if streak is not None:
        if not isinstance(streak, int):
            errors.append('streak must be an integer')
        elif streak < 0:
            errors.append('streak must be non-negative')

    completed_today = data.get('completed_today')
    if completed_today is not None and not isinstance(completed_today, bool):
        errors.append('completed_today must be a boolean')

    if errors:
        return None, JsonResponse({'errors': errors}, status=400)

    attrs = {}
    if name is not None:
        attrs['name'] = name.strip()
    if frequency is not None:
        attrs['frequency'] = frequency
    if streak is not None:
        attrs['streak'] = streak
    if completed_today is not None:
        attrs['completed_today'] = completed_today
    return attrs, None


# --- Task views ---

@require_http_methods(['GET', 'POST'])
def task_list(request):
    if request.method == 'GET':
        tasks = Task.objects.all().order_by('-created_at')
        status_param = request.GET.get('status')
        priority_param = request.GET.get('priority')
        errors = []
        if status_param is not None and status_param not in TASK_STATUSES:
            errors.append('status must be one of: not_started, in_progress, completed')
        if priority_param is not None and priority_param not in TASK_PRIORITIES:
            errors.append('priority must be one of: low, medium, high')
        if errors:
            return JsonResponse({'errors': errors}, status=400)
        if status_param is not None:
            tasks = tasks.filter(status=status_param)
        if priority_param is not None:
            tasks = tasks.filter(priority=priority_param)
        return JsonResponse([_serialize_task(t) for t in tasks], safe=False)
    # POST
    data, err = _parse_json(request)
    if err:
        return err
    attrs, err = _validate_task_data(data, for_update=False)
    if err:
        return err
    task = Task.objects.create(
        title=attrs['title'],
        description=attrs.get('description', ''),
        due_date=attrs.get('due_date'),
        priority=attrs.get('priority', Task.PRIORITY_MEDIUM),
        status=attrs.get('status', Task.STATUS_NOT_STARTED),
    )
    return JsonResponse(_serialize_task(task), status=201)


@require_http_methods(['GET', 'PUT', 'DELETE'])
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'GET':
        return JsonResponse(_serialize_task(task))
    if request.method == 'PUT':
        data, err = _parse_json(request)
        if err:
            return err
        attrs, err = _validate_task_data(data, for_update=True)
        if err:
            return err
        for key, value in attrs.items():
            setattr(task, key, value)
        task.save()
        return JsonResponse(_serialize_task(task))
    # DELETE
    task.delete()
    return HttpResponse(status=204)


# --- Habit views ---

@require_http_methods(['GET', 'POST'])
def habit_list(request):
    if request.method == 'GET':
        habits = Habit.objects.all().order_by('-created_at')
        frequency_param = request.GET.get('frequency')
        completed_param = request.GET.get('completed_today')
        errors = []
        if frequency_param is not None and frequency_param not in HABIT_FREQUENCIES:
            errors.append('frequency must be one of: daily, weekly')
        if completed_param is not None:
            if completed_param == 'true':
                completed_today_value = True
            elif completed_param == 'false':
                completed_today_value = False
            else:
                errors.append('completed_today must be true or false')
                completed_today_value = None
        else:
            completed_today_value = None
        if errors:
            return JsonResponse({'errors': errors}, status=400)
        if frequency_param is not None:
            habits = habits.filter(frequency=frequency_param)
        if completed_today_value is not None:
            habits = habits.filter(completed_today=completed_today_value)
        return JsonResponse([_serialize_habit(h) for h in habits], safe=False)
    # POST
    data, err = _parse_json(request)
    if err:
        return err
    attrs, err = _validate_habit_data(data, for_update=False)
    if err:
        return err
    habit = Habit.objects.create(
        name=attrs['name'],
        frequency=attrs.get('frequency', Habit.FREQUENCY_DAILY),
        streak=attrs.get('streak', 0),
        completed_today=attrs.get('completed_today', False),
    )
    return JsonResponse(_serialize_habit(habit), status=201)


@require_http_methods(['GET', 'PUT', 'DELETE'])
def habit_detail(request, pk):
    habit = get_object_or_404(Habit, pk=pk)
    if request.method == 'GET':
        return JsonResponse(_serialize_habit(habit))
    if request.method == 'PUT':
        data, err = _parse_json(request)
        if err:
            return err
        attrs, err = _validate_habit_data(data, for_update=True)
        if err:
            return err
        for key, value in attrs.items():
            setattr(habit, key, value)
        habit.save()
        return JsonResponse(_serialize_habit(habit))
    # DELETE
    habit.delete()
    return HttpResponse(status=204)
