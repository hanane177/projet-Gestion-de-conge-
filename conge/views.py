from django.shortcuts import render, redirect, get_object_or_404
from .forms import LeaveRequestForm, DepartmentForm
from .models import LeaveRequest, EmployeeLeaveBalance, LeaveType
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import LeaveBalance
from .forms import ReligiousHolidayForm  # Assurez-vous d'avoir un formulaire pour ce modèle
from django.http import HttpResponse
from .models import ReligiousHoliday
from .forms import ReligiousHolidayForm
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import calendar
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import Department  # Assurez-vous que le modèle Department existe
from .models import Report  # Assurez-vous que le modèle est importé et utilisé pour générer des rapports
from django.http import JsonResponse
from .models import Leave


def is_admin(user):
    return user.is_superuser
# Soumettre une demande de congé
@login_required
def submit_leave(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()
            messages.success(request, 'Demande de congé envoyée avec succès!')
            return redirect('leave_success')  # Replace with your success URL or view
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = LeaveRequestForm()
    
    return render(request, 'conge/submit_leave.html', {'form': form})

# Liste des demandes de congé avec pagination
@login_required
def leave_list(request):
    leave_requests = LeaveRequest.objects.all()
    leave_type = request.GET.get('type_conge', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')

    # Filter based on the type of leave
    if leave_type:
        leave_requests = leave_requests.filter(type_conge=leave_type)
    
    # Filter based on start and end dates
    if date_debut:
        leave_requests = leave_requests.filter(date_debut__gte=date_debut)
    if date_fin:
        leave_requests = leave_requests.filter(date_fin__lte=date_fin)

    # Paginate the results
    paginator = Paginator(leave_requests, 5)  # Show 5 leave requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Check if the user is an employee or admin
    is_employe = request.user.groups.filter(name='Employé').exists()
    is_admin = request.user.groups.filter(name='Administrateur').exists()

    # Render the template with the paginated leave requests and user roles
    return render(request, 'conge/leave_list.html', {
        'page_obj': page_obj,
        'is_employe': is_employe,
        'is_admin': is_admin,
    })

# Détails d'une demande de congé
@login_required
def leave_detail(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    return render(request, 'conge/leave_detail.html', {'leave_request': leave_request})

# Valider une demande de congé
@login_required
@user_passes_test(is_admin)
def valider_demande(request, id):
    demande = get_object_or_404(LeaveRequest, id=id)
    demande.statut = 'validé'
    demande.save()
    messages.success(request, 'Demande validée avec succès.')
    return redirect('leave_list')

# Rejeter une demande de congé
@login_required
@user_passes_test(is_admin)
def rejeter_demande(request, id):
    demande = get_object_or_404(LeaveRequest, id=id)
    demande.statut = 'rejeté'
    demande.save()
    messages.success(request, 'Demande rejetée avec succès.')
    return redirect('leave_list')

# Approuver une demande de congé
@login_required
def approve_leave_request(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if leave_request.statut != 'EN_ATTENTE':
        messages.error(request, 'La demande ne peut pas être approuvée.')
        return redirect('leave_list')
    
    leave_request.statut = 'validé'
    leave_request.save()

    # Mettre à jour le solde de congés de l'employé
    employee_balance = get_object_or_404(LeaveBalance, employee=leave_request.user)
    employee_balance.update_leave_balance(leave_request)

    messages.success(request, 'Demande approuvée avec succès.')
    return redirect('leave_list')

# Afficher le solde de congés
@login_required
def leave_balance(request):
    try:
        leave_balance = LeaveBalance.objects.get(employee=request.user)
    except LeaveBalance.DoesNotExist:
        leave_balance = None
    return render(request, 'conge/leave_balance.html', {'leave_balance': leave_balance})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def leave_calendar(request):
    events = [
        {"title": "Congé Annuel", "start": "2024-09-10", "end": "2024-09-15"},
        {"title": "Congé Maladie", "start": "2024-09-20", "end": "2024-09-22"}
    ]
    return render(request, 'conge/leave_calendar.html', {'events': json.dumps(events)})

# Ajouter un département
@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_department(request):
    if request.method == 'POST':
        department_name = request.POST.get('departmentName')
        department_description = request.POST.get('departmentDescription')
        
        # Création du nouveau département
        Department.objects.create(name=department_name, description=department_description)
        
        messages.success(request, "Département ajouté avec succès.")
        return redirect('conge/add_department')
    
    return render(request, 'conge/add_department.html')

def list_departments(request):
    departments = Department.objects.all()  # Récupère tous les départements
    return render(request, 'list_departments.html', {'departments': departments})

# Générer des rapports
@login_required
@user_passes_test(lambda u: u.is_superuser)
def generate_reports(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        reports = []

        # Vérification du type de rapport et génération des rapports
        if report_type == 'employees':
            reports = generate_employee_report(start_date, end_date)
        elif report_type == 'leaves':
            reports = generate_leave_report(start_date, end_date)
        else:
            messages.error(request, "Type de rapport invalide.")
        
        # Passer les rapports générés au template
        context = {
            'reports': reports,
        }
        messages.success(request, "Rapport généré avec succès.")
        return render(request, 'conge/generate_reports.html', context)

    return render(request, 'conge/generate_reports.html')

def generate_employee_report(start_date, end_date):
    # Exemple de génération de rapport des employés
    # Remplacez cette logique par votre propre logique pour générer un rapport
    return ["Employé 1", "Employé 2"]  # Exemple de données

def generate_leave_report(start_date, end_date):
    # Exemple de génération de rapport des congés
    # Remplacez cette logique par votre propre logique pour générer un rapport
    return ["Congé 1", "Congé 2"]  # Exemple de données
# Liste des types de congé
@login_required
def leave_type_list(request):
    leave_types = LeaveType.objects.all()
    return render(request, 'leave_type_list.html', {'leave_types': leave_types})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_religious_holidays(request):
    holidays = ReligiousHoliday.objects.all()
    return render(request, 'conge/manage_religious_holidays.html', {'holidays': holidays})

@login_required
def request_status(request):
    user_requests = LeaveRequest.objects.filter(user=request.user).order_by('-date_creation')
    return render(request, 'conge/request_status.html', {'requests': user_requests})

@login_required
def request_history(request):
    # Vérifiez si l'utilisateur est bien connecté
    if request.user.is_authenticated:
        user_requests = LeaveRequest.objects.filter(user=request.user, statut__in=['validé', 'rejeté'])
        context = {'requests': user_requests}
        return render(request, 'conge/request_history.html', context)
    else:
        return redirect('login')  # Redirigez l'utilisateur non authentifié vers la page de connexion



def leave_success(request):
    """
    Affiche une page de succès après la soumission d'une demande de congé.
    """
    return render(request, 'conge/leave_success.html')


def add_religious_holiday(request):
    if request.method == 'POST':
        form = ReligiousHolidayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fête religieuse ajoutée avec succès.")
            return redirect('manage_religious_holidays')
    else:
        form = ReligiousHolidayForm()
    return render(request, 'add_religious_holiday.html', {'form': form})

def edit_religious_holiday(request, pk):
    holiday = get_object_or_404(ReligiousHoliday, pk=pk)
    if request.method == 'POST':
        form = ReligiousHolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            return redirect('manage_religious_holidays')
    else:
        form = ReligiousHolidayForm(instance=holiday)
    return render(request, 'conge/edit_religious_holiday.html', {'form': form})

def delete_religious_holiday(request, pk):
    holiday = get_object_or_404(ReligiousHoliday, pk=pk)
    if request.method == 'POST':
        holiday.delete()
        return redirect('manage_religious_holidays')
    return render(request, 'conge/confirm_delete.html', {'holiday': holiday})

def delete_leave_request(request, pk):
    # Récupérer la demande de congé en fonction de l'utilisateur connecté et de l'ID
    leave_request = get_object_or_404(LeaveRequest, pk=pk, user=request.user)

    # Vérifier si le statut est "EN_ATTENTE"
    if leave_request.statut == 'EN_ATTENTE':
        leave_request.delete()
        messages.success(request, "Votre demande de congé a été supprimée avec succès.")
    else:
        messages.error(request, "Vous ne pouvez pas supprimer une demande qui a déjà été traitée.")
        return HttpResponseForbidden("Action non autorisée.")

    # Rediriger l'utilisateur vers la liste des demandes
    return redirect('leave_list')  # Assurez-vous que l'URL 'leave_list' est définie dans votre urls.py



def generate_pdf(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    static_url = request.build_absolute_uri('/static/')  # Absolute URL for static files


    # Rendre le template HTML pour le PDF
    html_string = render_to_string('conge/pdf_template.html', {
        'leave_request': leave_request,
        'static_url': static_url  # Pass static URL to template
    })
    # Créer une réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="decision_{leave_request.id}.pdf"'

    # Convertir HTML en PDF
    pisa_status = pisa.CreatePDF(html_string, dest=response)

    # Vérifier s'il y a eu des erreurs
    if pisa_status.err:
        messages.error(request, 'Une erreur est survenue lors de la génération du PDF.')
        return HttpResponse('Une erreur est survenue lors de la génération du PDF.')

    return response

def recalculate_leave_balance(employee):
    leave_balance, created = LeaveBalance.objects.get_or_create(employee=employee)
    approved_requests = LeaveRequest.objects.filter(user=employee, statut='APPROUVÉ')

    # Réinitialiser les soldes
    leave_balance.annual_leave_balance = 0
    leave_balance.sick_leave_balance = 0
    leave_balance.maternity_leave_balance = 0
    leave_balance.exceptional_leave_balance = 0

    # Calculer les soldes en fonction des demandes validées
    for request in approved_requests:
        if request.leave_type == 'annual':
            leave_balance.annual_leave_balance += request.number_of_days
        elif request.leave_type == 'sick':
            leave_balance.sick_leave_balance += request.number_of_days
        elif request.leave_type == 'maternity':
            leave_balance.maternity_leave_balance += request.number_of_days
        elif request.leave_type == 'exceptional':
            leave_balance.exceptional_leave_balance += request.number_of_days

    leave_balance.save()
    return leave_balance

def leave_balance_view(request):
    leave_balance = recalculate_leave_balance(request.user)
    return render(request, 'conge/leave_balance.html', {'leave_balance': leave_balance})

def get_leave_events(request):
    leaves = Leave.objects.all()  # Ajustez selon vos besoins
    events = []
    for leave in leaves:
        events.append({
            'title': leave.leave_type,
            'start': leave.start_date.isoformat(),
            'end': leave.end_date.isoformat()
        })
    return JsonResponse(events, safe=False)