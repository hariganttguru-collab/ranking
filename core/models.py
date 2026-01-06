from django.conf import settings
from django.db import models


class Stage(models.Model):
    """A configurable stage shown on the landing page and in the left menu."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, help_text="Optional image URL for the landing page card.")
    order = models.PositiveIntegerField(default=1, help_text="Order in which the stage is displayed.")

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    """A configurable task within a stage."""

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1, help_text="Order in which the task is displayed.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.stage.name} - {self.name}"


class TaskRanking(models.Model):
    """
    Stores a ranking value for a single task in a given stage by a specific user.

    For each (user, stage) pair, the ranks across tasks should be unique from 1..N.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="rankings")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="rankings")
    rank = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "stage", "task")
        ordering = ["stage", "rank"]

    def __str__(self) -> str:
        return f"{self.user} - {self.stage} - {self.task} -> {self.rank}"
