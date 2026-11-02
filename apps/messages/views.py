"""Представления личных сообщений."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.users.models import Notification, User, notify

from .forms import MessageForm
from .models import Conversation


@login_required
def inbox(request):
    """Список диалогов пользователя."""
    conversations = (
        Conversation.objects.filter(participants=request.user)
        .prefetch_related("participants")
        .order_by("-updated_at")
    )
    paginator = Paginator(conversations, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    for conversation in page_obj:
        conversation.partner = conversation.other_participant(request.user)
        conversation.unread = conversation.unread_count(request.user)
    return render(
        request,
        "messages/inbox.html",
        {"page_obj": page_obj, "total": paginator.count},
    )


@login_required
def conversation_detail(request, pk):
    """Страница диалога: переписка и форма отправки сообщения."""
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related("participants"), pk=pk
    )
    if not conversation.has_participant(request.user):
        raise PermissionDenied("Вы не участник этого диалога.")

    partner = conversation.other_participant(request.user)

    form = MessageForm()
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.recipient = partner
            message.save()
            Conversation.objects.filter(pk=conversation.pk).update(
                updated_at=message.created_at
            )
            notify(
                partner,
                title=f"Новое сообщение от {request.user.display_name}",
                body=message.content[:150],
                actor=request.user,
                type_=Notification.Type.NEW_MESSAGE,
                link=reverse("messages:detail", kwargs={"pk": conversation.pk}),
            )
            return redirect("messages:detail", pk=conversation.pk)

    conversation.messages.filter(recipient=request.user, is_read=False).update(
        is_read=True
    )

    return render(
        request,
        "messages/conversation.html",
        {
            "conversation": conversation,
            "partner": partner,
            "form": form,
            "message_list": conversation.messages.select_related("sender"),
        },
    )


@login_required
def conversation_start(request, user_pk):
    """Начать (или открыть существующий) диалог с пользователем."""
    partner = get_object_or_404(User, pk=user_pk)
    if partner.pk == request.user.pk:
        messages.info(request, "Нельзя написать самому себе.")
        return redirect("users:profile", pk=partner.pk)

    conversation, created = Conversation.get_or_create_between(request.user, partner)
    if created:
        messages.success(request, f"Диалог с {partner.display_name} создан.")
    return redirect("messages:detail", pk=conversation.pk)
