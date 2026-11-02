"""Формы приложения users."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm

from .models import PortfolioItem, User


def style_form(form):
    """Добавить полям формы CSS-классы для единообразной вёрстки."""
    for field in form.fields.values():
        widget = field.widget
        existing = widget.attrs.get("class", "")
        if isinstance(widget, forms.Textarea):
            css = "field field--textarea"
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            css = "field field--select"
        elif isinstance(widget, forms.CheckboxInput):
            css = "checkbox"
        elif isinstance(widget, forms.ClearableFileInput):
            css = "field field--file"
        else:
            css = "field"
        widget.attrs["class"] = f"{existing} {css}".strip()
    return form


class RegisterForm(UserCreationForm):
    """Регистрация с выбором роли."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["email"].label = "Электронная почта"
        self.fields["email"].required = True
        self.fields["role"].label = "Кто вы на бирже?"
        style_form(self)

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с такой почтой уже зарегистрирован.")
        return email


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class ProfileForm(forms.ModelForm):
    """Редактирование профиля пользователя."""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "role",
            "city",
            "skills",
            "telegram",
            "bio",
            "avatar",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        style_form(self)

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Этот адрес уже занят другим пользователем.")
        return email


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ("title", "description", "image", "link")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
