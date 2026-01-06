from django.contrib import admin

from .models import Stage, Task, TaskRanking


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)
    search_fields = ("name", "description")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "stage", "order", "is_active")
    list_filter = ("stage", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("name", "description")


@admin.register(TaskRanking)
class TaskRankingAdmin(admin.ModelAdmin):
    list_display = ("user", "stage", "task", "rank", "updated_at")
    list_filter = ("stage", "user")
