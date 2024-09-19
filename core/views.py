from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth import get_user_model, logout
from django.core.paginator import Paginator
from .forms import ContactForm, CustomUserCreationForm, CustomUserChangeForm, UserProfileForm
from .models import LeaveRequest, CustomUser, UserProfile
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

User = get_user_model()


@login_required
def home(request):
    if request.user.groups.filter(name='Administrateur').exists():
        return redirect('admin_dashboard')  # Remplacez par l'URL appropriée
    elif request.user.groups.filter(name='Responsable RH').exists():
        return redirect('hr_dashboard')  # Remplacez par l'URL appropriée
    elif request.user.groups.filter(name='Employé').exists():
        return redirect('employee_dashboard')  # Remplacez par l'URL appropriée
    else:
        return render(request, 'core/accueil.html')  # Page par défaut si aucun rôle n'est trouvé

def about(request):
    return render(request, 'core/about.html')

def service(request):
    return render(request, 'core/service.html')

def contact(request):
    return render(request, 'core/contact.html')
@login_required
def employee_dashboard(request):
    user = request.user
    if user.groups.filter(name='Employé').exists():
        # Debugging print statement
        print(f"User {user.username} has the 'Employé' group permission.")
        return render(request, 'core/employee_dashboard.html')
    else:
        # Debugging print statement
        print(f"User {user.username} does not have the 'Employé' group permission.")
        return redirect('home')


@login_required
@user_passes_test(lambda u: u.has_perm('core.can_manage_leave_requests'))
def hr_dashboard(request):
    leave_requests = LeaveRequest.objects.all()
    paginator = Paginator(leave_requests, 10)  # 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/hr_dashboard.html', {'page_obj': page_obj})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    users = User.objects.all()
    return render(request, 'core/admin_dashboard.html', {'users': users})

@login_required
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            try:
                send_mail(
                    f'Contact Form Submission from {name}',
                    message,
                    email,
                    ['votre_email@votreentreprise.com'],  # Replace with your email address
                    fail_silently=False,
                )
                messages.success(request, 'Merci de nous avoir contactés! Nous vous répondrons bientôt.')
                return redirect('contact')
            except Exception as e:
                messages.error(request, 'Une erreur est survenue lors de l\'envoi de votre message.')
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})

@login_required
@permission_required('auth.add_user', raise_exception=True)

def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            cin = form.cleaned_data.get('cin')
            if CustomUser.objects.filter(cin=cin).exists():
                form.add_error('cin', 'Cet utilisateur avec ce CIN existe déjà.')
            else:
                user = form.save()
                employe_group, created = Group.objects.get_or_create(name='Employé')
                user.groups.add(employe_group)
                return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/user_form.html', {'form': form})


@login_required
@permission_required('auth.change_user', raise_exception=True)
def update_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'core/user_form.html', {'form': form})

@login_required
@permission_required('auth.delete_user', raise_exception=True)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'core/user_confirm_delete.html', {'user': user})

@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'core/user_list.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def data_security(request):
    return render(request, 'core/data_security.html')

def generate_reports(request):
    # Logic to generate reports
    return render(request, 'core/generate_reports.html')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        messages.success(self.request, 'Vous êtes connecté avec succès!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erreur de connexion. Veuillez vérifier vos identifiants.')
        return super().form_invalid(form)

def custom_logout(request):
    logout(request)
    return redirect('login')  # Redirect to the login page


@login_required
def view_profile(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None
    return render(request, 'core/view_profile.html', {'user': user, 'profile': user_profile})


@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('view_profile')  # Redirige vers la page de profil après sauvegarde
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'core/edit_profile.html', {'form': form})




@login_required
def redirect_dashboard(request):
    user = request.user

    if user.groups.filter(name='Administrateur').exists():
        return redirect('admin_dashboard')  # Redirige vers le dashboard administrateur
    elif user.groups.filter(name='Responsable RH').exists():
        return redirect('hr_dashboard')  # Redirige vers le dashboard Responsable RH
    elif user.groups.filter(name='Employé').exists():
        return redirect('employee_dashboard')  # Redirige vers le dashboard Employé
    else:
        return redirect('default_dashboard')  # Redirige vers un tableau de bord par défaut ou une page d'erreur

