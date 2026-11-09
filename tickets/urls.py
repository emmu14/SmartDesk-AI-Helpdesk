from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.create_ticket, name='create_ticket'),
    path('dashboard/',views.employee_dashboard,name='dashboard'),
    path('agent-dashboard/',views.agent_dashboard,name='agent_dashboard'),
    path('update-status/<int:ticket_id>/',views.update_ticket_status,name='update_status'),
    path('<int:ticket_id>/comments/',views.ticket_comments,name='comments'),
    path('<int:ticket_id>/history/',views.ticket_history,name='history'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('predict-category/',views.predict_ticket_category,name='predict_category'),
    path('ai-analytics/',views.ai_analytics,name='ai_analytics'),
]