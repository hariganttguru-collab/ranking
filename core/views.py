from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .models import Stage, Task, TaskRanking, OfficialRanking


class RegisterView(View):
    """User registration view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("core:landing")
        return render(request, "registration/register.html")

    def post(self, request: HttpRequest) -> HttpResponse:
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")
        email = request.POST.get("email", "").strip()

        errors = []

        # Validation
        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username=username).exists():
            errors.append("Username already exists. Please choose a different one.")

        if not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if password != password_confirm:
            errors.append("Passwords do not match.")

        if errors:
            return render(
                request,
                "registration/register.html",
                {"errors": errors, "username": username, "email": email},
            )

        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email if email else "",
            )
            # Automatically log in the user after registration
            login(request, user)
            return redirect("core:landing")
        except Exception as e:
            errors.append(f"An error occurred: {str(e)}")
            return render(
                request,
                "registration/register.html",
                {"errors": errors, "username": username, "email": email},
            )


class LandingView(LoginRequiredMixin, View):
    """Landing page listing all stages as cards."""

    def get(self, request: HttpRequest) -> HttpResponse:
        stages = Stage.objects.all()
        return render(request, "core/landing.html", {"stages": stages})


class StageDetailView(LoginRequiredMixin, View):
    """
    Shows the selected stage, left menu with all stages, and ranking form for tasks.
    """

    def _calculate_score(self, user_rankings: dict, official_rankings: dict, total_tasks: int) -> dict:
        """
        Calculate score comparing user rankings to official rankings.
        Returns a dict with score details.
        """
        if not official_rankings or not user_rankings:
            return {
                "score": None,
                "exact_matches": 0,
                "total_tasks": total_tasks,
                "percentage": 0,
                "average_distance": None,
            }

        exact_matches = 0
        total_distance = 0
        matched_tasks = 0

        for task_id, user_rank in user_rankings.items():
            if task_id in official_rankings:
                official_rank = official_rankings[task_id]
                if user_rank == official_rank:
                    exact_matches += 1
                total_distance += abs(user_rank - official_rank)
                matched_tasks += 1

        if matched_tasks == 0:
            return {
                "score": None,
                "exact_matches": 0,
                "total_tasks": total_tasks,
                "percentage": 0,
                "average_distance": None,
            }

        percentage = (exact_matches / matched_tasks) * 100
        average_distance = total_distance / matched_tasks if matched_tasks > 0 else None

        # Score calculation: base score from exact matches, with penalty for distance
        # Max score is 100 (all exact matches)
        # Penalty: subtract points based on average distance
        base_score = percentage
        distance_penalty = average_distance * 5 if average_distance else 0  # 5 points per rank off
        final_score = max(0, base_score - distance_penalty)

        return {
            "score": round(final_score, 1),
            "exact_matches": exact_matches,
            "total_tasks": matched_tasks,
            "percentage": round(percentage, 1),
            "average_distance": round(average_distance, 2) if average_distance else None,
        }

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        stage = get_object_or_404(Stage, pk=pk)
        all_stages = Stage.objects.all()
        tasks = stage.tasks.filter(is_active=True)

        # Load existing rankings for this user + stage (if any)
        existing_rankings = {
            ranking.task_id: ranking.rank
            for ranking in TaskRanking.objects.filter(user=request.user, stage=stage)
        }

        # Load official rankings (set by superuser)
        official_rankings = {
            ranking.task_id: ranking.rank
            for ranking in OfficialRanking.objects.filter(stage=stage)
        }

        # Calculate score if user has rankings and official rankings exist
        score_data = None
        if existing_rankings and official_rankings:
            score_data = self._calculate_score(
                existing_rankings, official_rankings, tasks.count()
            )

        max_rank = tasks.count()
        rank_choices = list(range(1, max_rank + 1))

        context = {
            "current_stage": stage,
            "stages": all_stages,
            "tasks": tasks,
            "existing_rankings": existing_rankings,
            "rank_choices": rank_choices,
            "max_rank": max_rank,
            "score_data": score_data,
            "has_official_ranking": bool(official_rankings),
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
