# (C) 2025 Francesco Settembrini

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


# =============================================================================
# Form for user registration (Create)
# =============================================================================
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

# =============================================================================
# Form for profile updates (Update)
# =============================================================================
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']

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


