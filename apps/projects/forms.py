"""Формы приложения projects."""
from django import forms

from .models import Project


class ProjectCompleteForm(forms.ModelForm):
    """Завершение проекта с описанием результата."""

    class Meta:
        model = Project
        fields = ("summary",)
        widgets = {
            "summary": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Кратко опишите итог: что сделано, что передано заказчику",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["summary"].label = "Итог работы"
        self.fields["summary"].required = True
        self.fields["summary"].widget.attrs["class"] = "field field--textarea"


class ProjectCancelForm(forms.Form):
    """Отмена проекта с указанием причины."""

    reason = forms.CharField(
        label="Причина отмены",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "class": "field field--textarea"}),
    )
