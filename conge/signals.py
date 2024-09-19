from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LeaveRequest, LeaveBalance
from django.contrib.auth.models import User


@receiver(post_save, sender=LeaveRequest)
def update_leave_balance_on_approval(sender, instance, **kwargs):
    # Vérifier si la demande est approuvée
    if instance.statut == 'validé':
        try:
            employee_balance = LeaveBalance.objects.get(employee=instance.user)
            employee_balance.update_leave_balance(instance)
        except LeaveBalance.DoesNotExist:
            print("Le solde de congés pour cet utilisateur n'existe pas.")

@receiver(post_save, sender=User)
def create_leave_balance(sender, instance, created, **kwargs):
    if created:
        LeaveBalance.objects.create(employee=instance)
