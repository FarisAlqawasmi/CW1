from django.contrib import admin
from django.urls import reverse

from .models import Task, Habit


class TaskAdmin(admin.ModelAdmin):
    change_form_template = "admin/api/change_form_with_cancel.html"

    def change_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["cancel_url"] = reverse(
            "admin:api_task_changelist"
        )
        return super().change_view(request, object_id, form_url, extra_context)


class HabitAdmin(admin.ModelAdmin):
    change_form_template = "admin/api/change_form_with_cancel.html"

    def change_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["cancel_url"] = reverse(
            "admin:api_habit_changelist"
        )
        return super().change_view(request, object_id, form_url, extra_context)


admin.site.register(Task, TaskAdmin)
admin.site.register(Habit, HabitAdmin)
