from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_GET
from django.db import models
from django.db.models import Count, Avg, Q

from .forms import TicketStatusForm, CommentForm, TicketForm
from .models import Comment, Ticket, Category, AuditLog, TicketHistory
from .utils import record_ticket_history, assign_ticket
from .priority import predict_priority

from accounts.models import User
from notifications.utils import create_notification
from ai_engine.predict import predict_category
from django.db.models import Count, Avg, Q





@login_required
def create_ticket(request):

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.requester = request.user

            # AI category prediction
            prediction = predict_category(ticket.description)

            predicted_category = Category.objects.filter(
                name__iexact=prediction['category']
            ).first()
            confidence = prediction['confidence']
            # Store original AI prediction
            ticket.ai_predicted_category = predicted_category
            ticket.ai_prediction_confidence = confidence

            if not ticket.category and predicted_category and confidence >= 30:
                ticket.category = predicted_category

                # Check whether the final category differs from AI prediction
            ticket.ai_prediction_overridden = bool(
                ticket.category_id
                and predicted_category
                and ticket.category_id != predicted_category.id
            )
            # AI priority prediction
            ticket.priority = predict_priority(
                ticket.impact,
                ticket.urgency
            )

            ticket.save()
            


            AuditLog.objects.create(
                actor=request.user,
                ticket=ticket,
                action='Ticket Created',
                details=f"Ticket #{ticket.id} was created by {request.user.username}."
            )
           

            # Employee notification
            create_notification(
                request.user,
                f"Your ticket '{ticket.title}' has been created successfully."
            )

            # Ticket history
            record_ticket_history(
                ticket,
                request.user,
                'Created',
                'Ticket created by employee.'
            )

            # Automatic agent assignment
            agent = assign_ticket(ticket)

            if agent:
                ticket.assigned_agent = agent
                ticket.status = Ticket.Status.ASSIGNED

                ticket.save(
                    update_fields=[
                        'assigned_agent',
                        'status',
                        'updated_at'
                    ]
                )

                # Record automatic assignment in audit log
                AuditLog.objects.create(
                    actor=None,
                    ticket=ticket,
                    action='Ticket Automatically Assigned',
                    details=f'Ticket automatically assigned to {agent.username}.'
                )


                record_ticket_history(
                    ticket,
                    request.user,
                    'Assigned',
                    f'Ticket automatically assigned to {agent.username}.'
                )

                create_notification(
                    agent,
                    f'New ticket assigned to you: {ticket.title}'
                )

            messages.success(
                request,
                'Your ticket has been created successfully!'
            )

            return redirect('tickets:create_ticket')

    else:
        form = TicketForm()

    return render(
        request,
        'tickets/create_ticket.html',
        {'form': form}
    )



@login_required
@require_GET
def predict_ticket_category(request):

    description = request.GET.get('description', '').strip()

    if len(description) < 10:
        return JsonResponse({
            'error': 'Please enter at least 10 characters.'
        }, status=400)

    prediction = predict_category(description)

    return JsonResponse({
        'category': prediction['category'],
        'confidence': prediction['confidence']
    })





@login_required
def employee_dashboard(request):

    if request.user.role == 'agent':
        return redirect('tickets:agent_dashboard')

    if request.user.role == 'admin':
        return redirect('tickets:admin_dashboard')

    tickets = Ticket.objects.filter(
        requester=request.user
    ).order_by('-created_at')

    total_tickets = tickets.count()

    open_tickets = tickets.filter(
        status=Ticket.Status.OPEN
    ).count()

    resolved_tickets = tickets.filter(
        status=Ticket.Status.RESOLVED
    ).count()

    context = {
        'tickets': tickets,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'resolved_tickets': resolved_tickets,
    }

    return render(
        request,
        'tickets/employee_dashboard.html',
        context
    )

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Ticket


@login_required
def agent_dashboard(request):

    if request.user.role != 'agent':
        return HttpResponseForbidden(
            "You are not authorized to access this page."
        )

    tickets = Ticket.objects.filter(
        assigned_agent=request.user
    ).order_by('-created_at')

    total_tickets = tickets.count()

    pending_tickets = tickets.filter(
        status__in=['open', 'assigned']
    ).count()

    in_progress_tickets = tickets.filter(
        status='in_progress'
    ).count()

    resolved_tickets = tickets.filter(
        status='resolved'
    ).count()

    context = {
        'tickets': tickets,
        'total_tickets': total_tickets,
        'pending_tickets': pending_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
    }

    return render(
        request,
        'tickets/agent_dashboard.html',
        context
    )



@login_required
def update_ticket_status(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    if (
        request.user.role != 'agent'
        or ticket.assigned_agent_id != request.user.id
    ):
        return HttpResponseForbidden(
            "You cannot update this ticket."
        )

    if request.method == 'POST':

       
        old_status = ticket.status

        form = TicketStatusForm(
            request.POST,
            instance=ticket
        )

        if form.is_valid():

            updated_ticket = form.save()
            new_status = updated_ticket.status

            if old_status != new_status:

                AuditLog.objects.create(
                    actor=request.user,
                    ticket=ticket,
                    action='Ticket Status Changed',
                    details=(
                        f'Status changed from '
                        f'{old_status} to {new_status}.'
                    )
                )

                create_notification(
                    ticket.requester,
                    f"Your ticket '{ticket.title}' status changed "
                    f"to {ticket.get_status_display()}."
                )

                record_ticket_history(
                    ticket,
                    request.user,
                    'Status Changed',
                    f'Status changed from {old_status} to {new_status}.'
                )

                messages.success(
                    request,
                    'Ticket status updated successfully!'
                )

            else:
                messages.info(
                    request,
                    'No status change was made.'
                )

            return redirect('tickets:agent_dashboard')

    else:
        form = TicketStatusForm(instance=ticket)

    return render(
        request,
        'tickets/update_status.html',
        {
            'form': form,
            'ticket': ticket
        }
    )





@login_required
def ticket_comments(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    is_requester = ticket.requester_id == request.user.id

    is_assigned_agent = (
        ticket.assigned_agent_id == request.user.id
    )

    is_admin = request.user.role == 'admin'

    if not (is_requester or is_assigned_agent or is_admin):
        return HttpResponseForbidden(
            "You cannot access this ticket."
        )

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()

            AuditLog.objects.create(
                actor=request.user,
                ticket=ticket,
                action='Ticket Comment Added',
                details=f'{request.user.username} added a comment to ticket #{ticket.id}.'
            )
            record_ticket_history(
                ticket,
                request.user,
               'Comment Added',
               'A new comment was added to the ticket.'
            )

            messages.success(
               request,
               'Comment added successfully!'
            )

            return redirect(
                'tickets:comments',
                ticket_id=ticket.id
            )

    else:
        form = CommentForm()

    comments = ticket.comments.select_related(
        'author'
    ).order_by('created_at')

    return render(
        request,
        'tickets/ticket_comments.html',
        {
            'ticket': ticket,
            'comments': comments,
            'form': form
        }
    )


@login_required
def ticket_history(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    is_requester = ticket.requester_id == request.user.id
    is_assigned_agent = ticket.assigned_agent_id == request.user.id
    is_admin = request.user.role == 'admin'

    if not (is_requester or is_assigned_agent or is_admin):
        return HttpResponseForbidden(
            "You cannot access this history."
        )

    history = ticket.history.select_related(
        'user'
    ).order_by('-created_at')

    return render(
        request,
        'tickets/ticket_history.html',
        {
            'ticket': ticket,
            'history': history
        }
    )




@login_required
def admin_dashboard(request):

    if not (request.user.is_superuser or request.user.is_staff or request.user.role == 'admin'):
        return HttpResponseForbidden("Access denied")

    tickets = Ticket.objects.all().order_by('-created_at')

    total_tickets = tickets.count()
    open_tickets = tickets.filter(status='open').count()
    assigned_tickets = tickets.filter(status='assigned').count()
    in_progress_tickets = tickets.filter(status='in_progress').count()
    resolved_tickets = tickets.filter(status='resolved').count()
    closed_tickets = tickets.filter(status='closed').count()
    agents = User.objects.filter(
        role='agent',
        is_active=True
    ).annotate(
        total_assigned=Count('assigned_tickets'),
        active_tickets=Count(
            'assigned_tickets',
            filter=~Q(assigned_tickets__status__in=['resolved', 'closed'])
        ),
        resolved_tickets=Count(
            'assigned_tickets',
            filter=Q(assigned_tickets__status='resolved')
        ),
        closed_tickets=Count(
            'assigned_tickets',
            filter=Q(assigned_tickets__status='closed')
        )
    )

    agent_labels = [agent.username for agent in agents]

    agent_workload_data = [
        agent.active_tickets for agent in agents
    ]

    total_agents = agents.count()

    overloaded_agents = sum(
        1 for agent in agents
        if agent.active_tickets >= 10
    )

    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'assigned_tickets': assigned_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'agents': agents,
        'tickets': tickets[:10],
        'agent_labels': agent_labels,
        'agent_workload_data': agent_workload_data,
        'total_agents': total_agents,
        'overloaded_agents': overloaded_agents,
    }

    return render(request, 'tickets/admin_dashboard.html', context)


@login_required
def ai_analytics(request):

    if request.user.role != 'admin':
        return HttpResponseForbidden(
            "You are not authorized to access AI Analytics."
        )

    total_predictions = Ticket.objects.filter(
        ai_predicted_category__isnull=False
    ).count()

    overridden_predictions = Ticket.objects.filter(
        ai_prediction_overridden=True
    ).count()


    override_percentage = 0

    if total_predictions > 0:
        override_percentage = round(
            (overridden_predictions / total_predictions) * 100,
            2
        )


    matching_predictions = Ticket.objects.filter(
        ai_prediction_overridden=False,
        ai_predicted_category__isnull=False,
        category__isnull=False
    ).count()


    
    average_confidence = Ticket.objects.filter(
        ai_prediction_confidence__isnull=False
    ).aggregate(
        avg_confidence=Avg('ai_prediction_confidence')
    )['avg_confidence']

    if average_confidence is not None:
        average_confidence = round(float(average_confidence), 2)
    else:
        average_confidence = 0

    category_stats = (
        Ticket.objects
        .filter(ai_predicted_category__isnull=False)
        .values('ai_predicted_category__name')
        .annotate(
            total=Count('id'),
            overrides=Count(
                'id',
                filter=Q(ai_prediction_overridden=True)
            )
        )
        .order_by('-total')
    )

    for item in category_stats:
        item['override_rate'] = round(
            (item['overrides'] / item['total']) * 100,
            2
        ) if item['total'] > 0 else 0

    context = {
        'total_predictions': total_predictions,
        'overridden_predictions': overridden_predictions,
        'matching_predictions': matching_predictions,
        'category_stats': category_stats,
        'average_confidence': average_confidence,
        'override_percentage': override_percentage,



        'category_labels': [
            item['ai_predicted_category__name']
            for item in category_stats
        ],

        'category_values': [
            item['total']
            for item in category_stats
        ],

        'chart_data': [
            matching_predictions,
            overridden_predictions
        ]
    }

    return render(
        request,
        'tickets/ai_analytics.html',
        context
    )