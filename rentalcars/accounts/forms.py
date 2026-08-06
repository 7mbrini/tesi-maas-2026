# (C) 2026 Francesco Settembrini

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


# =============================================================================
# Form per la user registration (Create)
# =============================================================================
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

# =============================================================================
# Form per l'agiornamento dell'account
# =============================================================================
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']

# =============================================================================
# Form per la modifica di nome, cognome ed email
# =============================================================================
class UserProfileEditForm(UserChangeForm):

    class Meta:
        model = User

        fields = [
            'first_name',
            'last_name',
            'email',
        ]

        exclude = ('password',)


