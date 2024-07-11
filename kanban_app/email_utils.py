from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_project_assigned_email(project_name, users):
    subject = f'New Project Assigned: {project_name}'
    html_message = render_to_string('emails/project_assigned.html', {'project_name': project_name})
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email for user in users if user.email]  # Ensure users have email addresses

    send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        html_message=html_message,
    )


def send_newuser_register_email(user_data):
    subject = f'Your new account has been created.'
    context ={
        'username': user_data['username'],
        'email': user_data['email'],
        'password': user_data['password'],
        'role': user_data['role'],
    }
    html_message = render_to_string('emails/newuser_register.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_data['email']]

    send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        html_message=html_message,
    )