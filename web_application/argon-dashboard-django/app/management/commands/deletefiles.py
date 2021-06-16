from django.core.management.base import BaseCommand
import datetime
from app.models import File
from django.contrib.auth.models import User
from datetime import timezone
class Command(BaseCommand):
    help = 'Deletes dummy files from db.'

    def handle(self, *args, **kwargs):
        time = datetime.datetime.now(timezone.utc)
        dummy_user = User.objects.get(username='dummy_user')
        files = File.objects.all().filter(user=dummy_user)

        for f in files:
            diff = time - f.uploaded_time
            if diff > datetime.timedelta(hours=10):
                File.objects.get(file_name=f.file_name).delete()
                self.stdout.write("File " + f.file_name + " successfully deleted.")

        self.stdout.write("deleted.")