from django.test import TestCase
from django.urls import reverse


class AdminDashboardTests(TestCase):

    def test_admin_dashboard_requires_login(self):
        response = self.client.get(
            reverse('tickets:admin_dashboard')
        )

        self.assertEqual(response.status_code, 302)

    def test_employee_cannot_access_admin_dashboard(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        employee = User.objects.create_user(
            username='testemployee',
            password='testpass123',
            role='employee'
        )

        self.client.login(
            username='testemployee',
            password='testpass123'
        )

        response = self.client.get(
            reverse('tickets:admin_dashboard')
        )

        self.assertEqual(response.status_code, 403)    

    def test_admin_can_access_admin_dashboard(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        admin = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            role='admin'
        )

        self.client.login(
            username='testadmin',
            password='testpass123'
        )

        response = self.client.get(
            reverse('tickets:admin_dashboard')
        )

        self.assertEqual(response.status_code, 200)    

    def test_employee_cannot_access_agent_dashboard(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        employee = User.objects.create_user(
            username='agent_test_employee',
            password='testpass123',
            role='employee'
        )

        self.client.login(
            username='agent_test_employee',
            password='testpass123'
        )

        response = self.client.get(
            reverse('tickets:agent_dashboard')
        )

        self.assertEqual(response.status_code, 403)    

    def test_agent_can_access_agent_dashboard(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        agent = User.objects.create_user(
            username='test_agent',
            password='testpass123',
            role='agent'
        )

        self.client.login(
            username='test_agent',
            password='testpass123'
        )

        response = self.client.get(
            reverse('tickets:agent_dashboard')
        )

        self.assertEqual(response.status_code, 200)    

    def test_employee_sees_only_own_tickets(self):
        from django.contrib.auth import get_user_model
        from .models import Ticket

        User = get_user_model()

        employee1 = User.objects.create_user(
            username='employee_one',
            password='testpass123',
            role='employee'
        )

        employee2 = User.objects.create_user(
            username='employee_two',
            password='testpass123',
            role='employee'
        )


        Ticket.objects.create(
            title='Employee One Ticket',
            description='This is employee one ticket',
            requester=employee1
        )

        Ticket.objects.create(
            title='Employee Two Ticket',
            description='This is employee two ticket',
            requester=employee2
        )

        self.client.login(
            username='employee_one',
            password='testpass123'
        )

        response = self.client.get(
            reverse('tickets:dashboard')
        )

        self.assertEqual(response.status_code, 200)

        visible_tickets = response.context['tickets']

        self.assertEqual(visible_tickets.count(), 1)

        self.assertEqual(
            visible_tickets.first().title,
            'Employee One Ticket'
        )

        self.assertEqual(
            visible_tickets.first().requester,
            employee1
        )