from .models import TicketHistory
from .models import Ticket , AuditLog
from accounts.models import User
from django.utils import timezone



def record_ticket_history(ticket, user, action, details=''):

    TicketHistory.objects.create(
        ticket=ticket,
        user=user,
        action=action,
        details=details
    )


def assign_ticket(ticket):

    agents = User.objects.filter(
        role='agent',
        is_active=True
    )

    if not agents.exists():
        return None

    old_agent = ticket.assigned_agent

    selected_agent = min(
        agents,
        key=lambda agent: (
            Ticket.objects.filter(
                assigned_agent=agent
            ).exclude(
                status__in=['resolved', 'closed']
            ).count(),
            agent.last_assigned_at is not None,
            agent.last_assigned_at
        )
    )

    selected_agent.last_assigned_at = timezone.now()
    selected_agent.save(update_fields=['last_assigned_at'])

    ticket.assigned_agent = selected_agent
    ticket.status = 'assigned'
    ticket.save()

    if old_agent != selected_agent:

        AuditLog.objects.create(
            actor=None,
            ticket=ticket,
            action='Ticket Automatically Assigned',
            details=(
                f'Ticket #{ticket.id} was assigned to '
                f'{selected_agent.username}.'
            )
        )

        record_ticket_history(
            ticket,
            None,
            'Agent Assigned',
            f'Ticket automatically assigned to {selected_agent.username}.'
        )

    return selected_agent