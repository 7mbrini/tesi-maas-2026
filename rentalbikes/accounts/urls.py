# (C) 2025 Francesco Settembrini

from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView # <-- Import these
from .views import (
    UserRegisterView,
    UserListView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    logout_view,
    edit_profile,
    registration_success,
)

urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),

    # CRUD Views
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('registration-success/', registration_success, name='registration_success'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('', UserListView.as_view(), name='user_list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    # URL per cambiare la password (richiede login)
    path('change-password/',
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/change_password.html',
             success_url='/accounts/'  # Redirect se successo
         ),
         name='change_password'),
]

