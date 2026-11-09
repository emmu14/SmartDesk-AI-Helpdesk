from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Notification


@login_required
def notification_list(request):

    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    unread_count = notifications.filter(
        is_read=False
    ).count()

    return render(
        request,
        'notifications/notification_list.html',
        {
            'notifications': notifications,
            'unread_count': unread_count,
        }
    )

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST


@login_required
@require_POST
def mark_as_read(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    return redirect('notifications:list')