# user/management/commands/createadmin.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates an admin user'

    def handle(self, *args, **kwargs):
        email = 'admin@gmail.com'
        name = 'admin'
        role = 'administrator'  # Assuming the role for an admin user
        gender = 'male'
        
        register_no = 'wan1'
        contact_number = '1234567890'
        password = 'admin'

        try:
            user = User.objects.create_superuser(
                email=email,
                name=name,
                # role=role,
                # gender=gender,
                register_no=register_no,
                # contact_number=contact_number,
                password=password
            )
            self.stdout.write(self.style.SUCCESS('Admin user created successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to create admin user: {str(e)}'))