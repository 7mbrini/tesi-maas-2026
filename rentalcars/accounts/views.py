# (C) 2026 Francesco Settembrini

from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

from .forms import CustomUserCreationForm, CustomUserChangeForm, UserProfileEditForm


# CRUD

# --- Create (Registration) ---
class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('registration_success')

# --- Read (Elenca tutti gli users) ---
class UserListView(ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

# --- Read (User Detail/Profile) ---
class UserDetailView(DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'

# --- Update (Aggiorna lo User Profile) ---
class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/user_update.html'
    success_url = reverse_lazy('user_list')

    # solo user o superuser (admin) possono aggiornare
    def test_func(self):
        user_obj = self.get_object()
        return self.request.user == user_obj or self.request.user.is_superuser

# --- Delete (User Account Deletion) ---
class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'accounts/user_delete.html'
    success_url = reverse_lazy('user_list')

    # soltanto owner or superuser possono effettuare il "delete"
    def test_func(self):
        user_obj = self.get_object()
        return self.request.user == user_obj or self.request.user.is_superuser

def logout_view(request):
    logout(request)
    return render(request, 'accounts/logout.html')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Passiamo l'istanza dell'utente corrente al form
        form = UserProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been successfully updated!')
            return redirect('edit_profile')  # Reindirizza alla stessa pagina o a una pagina di successo
    else:
        # Quando carichiamo la pagina, prepopoliamo il form con i dati correnti
        form = UserProfileEditForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


# mostra il messaggio di conferma della registrazione
def registration_success(request):
    return render(request, 'accounts/registration_success.html')

# View personalizzata per il cambio password
class UserPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'accounts/change_password.html'
    success_url = '/accounts/'
