"""Формы приложения reviews."""
from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """Форма отзыва: оценка звёздами + текст."""

    RATING_CHOICES = [(i, "★" * i + f" ({i})") for i in range(1, 6)]

    class Meta:
        model = Review
        fields = ("rating", "comment")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rating"] = forms.ChoiceField(
            label="Оценка", choices=self.RATING_CHOICES, widget=forms.RadioSelect
        )
        self.fields["comment"] = forms.CharField(
            label="Текст отзыва",
            widget=forms.Textarea(
                attrs={"rows": 5, "placeholder": "Как прошла работа, что получилось хорошо"}
            ),
            min_length=10,
        )
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "field field--textarea")
