from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .models import Stage, Task, TaskRanking


class LandingView(LoginRequiredMixin, View):
    """Landing page listing all stages as cards."""

    def get(self, request: HttpRequest) -> HttpResponse:
        stages = Stage.objects.all()
        return render(request, "core/landing.html", {"stages": stages})


class StageDetailView(LoginRequiredMixin, View):
    """
    Shows the selected stage, left menu with all stages, and ranking form for tasks.
    """

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        stage = get_object_or_404(Stage, pk=pk)
        all_stages = Stage.objects.all()
        tasks = stage.tasks.filter(is_active=True)

        # Load existing rankings for this user + stage (if any)
        existing_rankings = {
            ranking.task_id: ranking.rank
            for ranking in TaskRanking.objects.filter(user=request.user, stage=stage)
        }

        max_rank = tasks.count()
        rank_choices = list(range(1, max_rank + 1))

        context = {
            "current_stage": stage,
            "stages": all_stages,
            "tasks": tasks,
            "existing_rankings": existing_rankings,
            "rank_choices": rank_choices,
            "max_rank": max_rank,
        }
        return render(request, "core/stage_detail.html", context)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        stage = get_object_or_404(Stage, pk=pk)
        tasks = list(stage.tasks.filter(is_active=True))
        max_rank = len(tasks)
        rank_field_prefix = "rank_"

        # Collect submitted ranks
        submitted_ranks = {}
        for task in tasks:
            field_name = f"{rank_field_prefix}{task.id}"
            raw_value = request.POST.get(field_name)
            if raw_value:
                try:
                    rank_val = int(raw_value)
                except ValueError:
                    continue
                if 1 <= rank_val <= max_rank:
                    submitted_ranks[task.id] = rank_val

        # Basic validation: all tasks ranked, and ranks unique
        errors = []
        if len(submitted_ranks) != len(tasks):
            errors.append("Please provide a unique rank for every task.")
        if len(set(submitted_ranks.values())) != len(submitted_ranks.values()):
            errors.append("Each rank value must be used exactly once.")

        if errors:
            all_stages = Stage.objects.all()
            context = {
                "current_stage": stage,
                "stages": all_stages,
                "tasks": tasks,
                "existing_rankings": submitted_ranks,
                "rank_choices": list(range(1, max_rank + 1)),
                "max_rank": max_rank,
                "errors": errors,
            }
            return render(request, "core/stage_detail.html", context)

        # Save rankings: upsert for each task
        for task in tasks:
            rank_val = submitted_ranks.get(task.id)
            if rank_val is None:
                continue
            TaskRanking.objects.update_or_create(
                user=request.user,
                stage=stage,
                task=task,
                defaults={"rank": rank_val},
            )

        return redirect(reverse("core:stage_detail", args=[stage.id]))
