from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from datetime import date
import datetime


class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du Type de Congé")

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    STATUTS = [
        ('EN_ATTENTE', 'En attente'),
        ('APPROUVÉ', 'Approuvé'),
        ('REJETÉ', 'Rejeté'),
    ]

    TYPES_CONGES = [
        ('annual', 'Congé Annuel'),
        ('exceptional', 'Congé Exceptionnel'),
        ('pilgrimage', 'Congé pour pèlerinage'),
        ('sick', 'Congé de Maladie'),
        ('maternity', 'Congé de Maternité'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type_conge = models.ForeignKey('LeaveType', on_delete=models.CASCADE, verbose_name="Type de congé")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    motif = models.TextField(default="Aucun motif fourni", verbose_name="Motif")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    statut = models.CharField(max_length=10, choices=STATUTS, default='EN_ATTENTE', verbose_name="Statut")

    def clean(self):
       if self.date_debut is None or self.date_fin is None:
        raise ValidationError('Les dates de début et de fin doivent être fournies.')
       if self.date_fin < self.date_debut:
        raise ValidationError('La date de fin ne peut pas être antérieure à la date de début.')

    def nombre_jours(self):
        return (self.date_fin - self.date_debut).days + 1

    def __str__(self):
        return f"Demande de {self.type_conge} de {self.date_debut} à {self.date_fin} - Statut: {self.get_statut_display()}"
    
class EmployeeLeaveBalance(models.Model):
    LEAVE_TYPES = {
        'annual': 'annual_leave_balance',
        'sick': 'sick_leave_balance',
        'maternity': 'maternity_leave_balance',
        'exceptional': 'exceptional_leave_balance'
    }
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    annual_leave_balance = models.PositiveIntegerField(default=0)
    sick_leave_balance = models.PositiveIntegerField(default=0)
    maternity_leave_balance = models.PositiveIntegerField(default=0)
    exceptional_leave_balance = models.PositiveIntegerField(default=0)
    
    def update_leave_balance(self, leave_request):
        leave_type = leave_request.type_conge.name.lower()
        if leave_type in self.LEAVE_TYPES:
            field = self.LEAVE_TYPES[leave_type]
            current_balance = getattr(self, field)
            setattr(self, field, current_balance - leave_request.nombre_jours())
            self.save()
    
    def __str__(self):
        return f"Soldes de congés pour {self.employee.username}"
    
class Command(BaseCommand):
    help = 'Réinitialiser les soldes de congés annuels'

    def handle(self, *args, **options):
        # Réinitialiser les soldes de congés annuels (par exemple, ajouter 22 jours)
        for balance in EmployeeLeaveBalance.objects.all():
            balance.annual_leave_balance = 22
            balance.save()
        self.stdout.write(self.style.SUCCESS('Soldes annuels réinitialisés avec succès.'))

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class LeaveBalance(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    annual_leave_balance = models.PositiveIntegerField(default=0)
    sick_leave_balance = models.PositiveIntegerField(default=0)
    maternity_leave_balance = models.PositiveIntegerField(default=0)
    exceptional_leave_balance = models.PositiveIntegerField(default=0)

    def update_leave_balance(self, leave_request):
        if leave_request.statut == 'validé':
            if leave_request.leave_type == 'annual':
                self.annual_leave_balance -= leave_request.number_of_days
            elif leave_request.leave_type == 'sick':
                self.sick_leave_balance -= leave_request.number_of_days
            elif leave_request.leave_type == 'maternity':
                self.maternity_leave_balance -= leave_request.number_of_days
            elif leave_request.leave_type == 'exceptional':
                self.exceptional_leave_balance -= leave_request.number_of_days
            self.save()

    def __str__(self):
        return f'{self.employee.username} - Solde des congés'
class ReligiousHoliday(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    
class Report(models.Model):
    report_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    content = models.TextField()  # Exemple de champ pour stocker le contenu du rapport

class Leave(models.Model):
    leave_type = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.leave_type} from {self.start_date} to {self.end_date}"