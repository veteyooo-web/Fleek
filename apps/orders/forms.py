"""Формы приложения orders."""
from django import forms
from django.db.models import Q

from .models import Category, Order


class OrderForm(forms.ModelForm):
    """Создание заказа."""

    publish_later = forms.BooleanField(
        required=False, label="Сохранить как черновик (не публиковать)"
    )

    class Meta:
        model = Order
        fields = ("title", "description", "category", "budget_min", "budget_max", "deadline", "skills")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Например: Нужен лендинг для кофейни"}),
            "description": forms.Textarea(
                attrs={"rows": 8, "placeholder": "Опишите задачу, требования и ожидаемый результат"}
            ),
            "category": forms.Select(),
            "budget_min": forms.NumberInput(attrs={"min": 0, "step": 100}),
            "budget_max": forms.NumberInput(attrs={"min": 0, "step": 100}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "skills": forms.TextInput(attrs={"placeholder": "Python, Django, Figma"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            base = widget.attrs.get("class", "")
            if isinstance(widget, forms.CheckboxInput):
                css = "checkbox"
            elif isinstance(widget, forms.Textarea):
                css = "field field--textarea"
            elif isinstance(widget, forms.Select):
                css = "field field--select"
            else:
                css = "field"
            widget.attrs["class"] = f"{base} {css}".strip()

    def clean(self):
        cleaned = super().clean()
        low = cleaned.get("budget_min") or 0
        high = cleaned.get("budget_max") or 0
        if low and high and low > high:
            self.add_error("budget_max", "Верхняя граница бюджета не может быть меньше нижней.")
        return cleaned

    def save(self, commit=True):
        order = super().save(commit=False)
        # publish_later есть только в форме создания заказа
        if self.cleaned_data.get("publish_later"):
            order.status = Order.Status.DRAFT
        elif "publish_later" in self.fields:
            order.status = Order.Status.OPEN
        if commit:
            order.save()
        return order


class OrderUpdateForm(OrderForm):
    """Редактирование заказа владельцем."""

    status = forms.ChoiceField(
        label="Статус",
        choices=[
            (Order.Status.DRAFT, "Черновик"),
            (Order.Status.OPEN, "Открыт"),
            (Order.Status.CANCELLED, "Отменён"),
        ],
        widget=forms.Select(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("publish_later", None)
        self.fields["status"].initial = self.instance.status
        self.fields["status"].widget.attrs["class"] = "field field--select"

    def save(self, commit=True):
        order = super(OrderUpdateForm, self).save(commit=False)
        if self.cleaned_data.get("status"):
            order.status = self.cleaned_data["status"]
        if commit:
            order.save()
        return order


class OrderSearchForm(forms.Form):
    """Поиск и фильтрация списка заказов."""

    SORT_CHOICES = [
        ("-created_at", "Сначала новые"),
        ("created_at", "Сначала старые"),
        ("-budget_max", "Сначала дорогие"),
        ("budget_max", "Сначала дешёвые"),
    ]

    q = forms.CharField(label="Поиск", required=False)
    category = forms.ModelChoiceField(
        label="Категория", queryset=Category.objects.all(), required=False, empty_label="Все категории"
    )
    status = forms.ChoiceField(label="Статус", required=False, choices=[("", "Любой статус")] + Order.Status.choices)
    min_budget = forms.DecimalField(label="Бюджет от", required=False, min_value=0, decimal_places=0)
    max_budget = forms.DecimalField(label="Бюджет до", required=False, min_value=0, decimal_places=0)
    sort = forms.ChoiceField(label="Сортировка", required=False, choices=SORT_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = "field field--select" if isinstance(field.widget, forms.Select) else "field"
            field.widget.attrs["class"] = css

    def filter_queryset(self, queryset):
        data = self.cleaned_data
        if not data.get("q"):
            pass
        else:
            query = data["q"]
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(skills__icontains=query)
            )
        if data.get("category"):
            queryset = queryset.filter(category=data["category"])
        if data.get("status"):
            queryset = queryset.filter(status=data["status"])
        if data.get("min_budget"):
            queryset = queryset.filter(budget_max__gte=data["min_budget"])
        if data.get("max_budget"):
            queryset = queryset.filter(budget_min__lte=data["max_budget"])
        sort = data.get("sort") or self.SORT_CHOICES[0][0]
        return queryset.order_by(sort).distinct()
