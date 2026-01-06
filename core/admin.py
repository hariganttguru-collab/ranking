from django.contrib import admin

from .models import Stage, Task, TaskRanking, OfficialRanking


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


@admin.register(OfficialRanking)
class OfficialRankingAdmin(admin.ModelAdmin):
    list_display = ("stage", "task", "rank", "updated_at")
    list_filter = ("stage",)
    search_fields = ("task__name", "stage__name")
    ordering = ("stage", "rank")

    def has_add_permission(self, request):
        """Only superusers can set official rankings."""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Only superusers can change official rankings."""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete official rankings."""
        return request.user.is_superuser


@admin.register(TaskRanking)
class TaskRankingAdmin(admin.ModelAdmin):
    list_display = ("user", "stage", "task", "rank", "updated_at")
    list_filter = ("stage", "user")
