# (C) 2026 Francesco Settembrini

from django.urls import path

from . import views


urlpatterns = [
    path('login/', views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # CRUD Views
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('', views.UserListView.as_view(), name='user_list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('change-password/', views.UserPasswordChangeView.as_view(), name='change_password'),
]

