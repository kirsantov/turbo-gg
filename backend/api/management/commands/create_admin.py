from django.core.management.base import BaseCommand
from api.models import User


class Command(BaseCommand):
    help = 'Create superuser with default credentials'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.SUCCESS('Admin user already exists'))
            # Update password
            user = User.objects.get(username='admin')
            user.set_password('admin')
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS('Admin password reset to: admin'))
        else:
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created admin user'))
            self.stdout.write(self.style.SUCCESS('Username: admin'))
            self.stdout.write(self.style.SUCCESS('Password: admin'))
