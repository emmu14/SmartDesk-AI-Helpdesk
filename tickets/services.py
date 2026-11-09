from django.db.models import Count, Q
from accounts.models import User
from .models import Ticket
from notifications.utils import create_notification


def assign_ticket(ticket):

    active_statuses = [
        Ticket.Status.OPEN,
        Ticket.Status.ASSIGNED,
        Ticket.Status.IN_PROGRESS,
    ]

    agents = User.objects.filter(
        role=User.Role.AGENT,
        is_active=True
    )

    if ticket.department:
        agents = agents.filter(
            department=ticket.department
        )

    agents = agents.annotate(
        active_ticket_count=Count(
            'assigned_tickets',
            filter=Q(
                assigned_tickets__status__in=active_statuses
            )
        )
    ).order_by('active_ticket_count', 'id')

    agent = agents.first()

    if agent:
        ticket.assigned_agent = agent
        ticket.status = Ticket.Status.ASSIGNED

        ticket.save(
            update_fields=['assigned_agent', 'status', 'updated_at']
        )
        create_notification(
              agent,
              f"You have been assigned a new ticket: {ticket.title}"
)

    return agent