"""Представления приложения reviews."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.projects.models import Project

from .forms import ReviewForm
from .models import Review


@login_required
def review_create(request, project_pk):
    """Оставить отзыв о партнёре по завершённому проекту."""
    project = get_object_or_404(Project, pk=project_pk)
    if not project.is_participant(request.user) and not request.user.is_superuser:
        raise PermissionDenied("Отзыв может оставить только участник проекта.")
    if project.status != Project.Status.COMPLETED:
        messages.error(request, "Оставлять отзыв можно только после завершения проекта.")
        return redirect("projects:detail", pk=project.pk)
    if project.reviews.filter(author=request.user).exists():
        messages.info(request, "Вы уже оставили отзыв по этому проекту.")
        return redirect("projects:detail", pk=project.pk)

    target = (
        project.customer
        if request.user.pk == project.freelancer_id
        else project.freelancer
    )

    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        review.target = target
        review.project = project
        review.save()
        messages.success(request, f"Спасибо! Отзыв о {target.display_name} опубликован.")
        return redirect("users:profile", pk=target.pk)

    return render(
        request,
        "reviews/review_form.html",
        {"form": form, "project": project, "target": target},
    )


@login_required
def review_delete(request, pk):
    """Удалить собственный отзыв."""
    review = get_object_or_404(Review.objects.select_related("target"), pk=pk)
    if review.author_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Удалить отзыв может только его автор.")
    if request.method == "POST":
        target_pk = review.target_id
        review.delete()
        messages.success(request, "Отзыв удалён.")
        return redirect("users:profile", pk=target_pk)
    return render(request, "reviews/review_confirm_delete.html", {"review": review})


def latest(request):
    """Страница последних отзывов на бирже."""
    reviews = Review.objects.select_related("author", "target", "project").order_by(
        "-created_at"
    )
    paginator = Paginator(reviews, 15)
    return render(
        request,
        "reviews/review_list.html",
        {"page_obj": paginator.get_page(request.GET.get("page"))},
    )
