from django.contrib import admin
from .models import Ticket, Category, Comment, TicketHistory, AuditLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)



@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'title',
        'category',
        'ai_predicted_category',
        'ai_prediction_confidence',
        'ai_prediction_overridden',
        'status',
        'priority',
    )

    list_filter = (
        'category',
        'ai_predicted_category',
        'ai_prediction_overridden',
        'status',
        'priority',
    )

    search_fields = (
        'title',
        'description',
    )

    readonly_fields = (
        'ai_predicted_category',
        'ai_prediction_confidence',
        'ai_prediction_overridden',
    )

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'actor',
        'ticket',
        'action',
        'created_at',
    )

    list_filter = (
        'action',
        'created_at',
    )

    search_fields = (
        'action',
        'details',
        'actor__username',
    )

    readonly_fields = (
        'actor',
        'ticket',
        'action',
        'details',
        'created_at',
    )

    ordering = ('-created_at',)



admin.site.register(Comment)
admin.site.register(TicketHistory)    