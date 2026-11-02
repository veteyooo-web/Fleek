"""Формы приложения applications."""
from django import forms
from django.core.exceptions import ValidationError

from apps.orders.models import Order

from .models import Application


class ApplicationForm(forms.ModelForm):
    """Отправка отклика на заказ."""

    class Meta:
        model = Application
        fields = ("price", "days", "cover_letter")
        widgets = {
            "price": forms.NumberInput(attrs={"min": 1, "step": 100, "placeholder": "Например: 25000"}),
            "days": forms.NumberInput(attrs={"min": 1, "step": 1, "placeholder": "Например: 10"}),
            "cover_letter": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Расскажите, почему именно вы подходите для этого заказа",
                }
            ),
        }

    def __init__(self, *args, order=None, freelancer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = order or getattr(self.instance, "order", None)
        self.freelancer = freelancer or getattr(self.instance, "freelancer", None)
        self.fields["price"].label = "Ваша цена, ₽"
        self.fields["days"].label = "Срок выполнения, дней"
        self.fields["cover_letter"].label = "Сообщение заказчику"
        for name, field in self.fields.items():
            css = "field field--textarea" if isinstance(field.widget, forms.Textarea) else "field"
            field.widget.attrs.setdefault("class", css)
        if self.order is not None:
            self.fields["price"].initial = self.order.budget_min or None

    def clean(self):
        cleaned = super().clean()
        order = self.order
        if order is None:
            raise ValidationError("Не указан заказ, на который отправляется отклик.")
        if order.status != Order.Status.OPEN:
            raise ValidationError("Этот заказ больше не принимает отклики.")
        if self.freelancer is not None and order.owner_id == self.freelancer.pk:
            raise ValidationError("Нельзя откликнуться на собственный заказ.")
        if (
            self.freelancer is not None
            and Application.objects.filter(order=order, freelancer=self.freelancer)
            .exclude(pk=self.instance.pk if self.instance.pk else None)
            .exists()
        ):
            raise ValidationError("Вы уже отправляли отклик на этот заказ.")
        return cleaned

    def save(self, commit=True):
        application = super().save(commit=False)
        application.order = self.order
        application.freelancer = self.freelancer
        if commit:
            application.save()
        return application
