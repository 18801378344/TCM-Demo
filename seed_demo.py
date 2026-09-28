"""Create two ordinary reviewers without exposing credentials in source/logs."""
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.production")
django.setup()
from django.contrib.auth import get_user_model
from django.db import transaction
from documents.models import Document

with transaction.atomic():
    for number in (1, 2):
        password = os.environ[f"DEMO_PASSWORD_{number}"]
        if len(password) < 16:
            raise ValueError("Demo passwords must contain at least 16 characters")
        user, created = get_user_model().objects.get_or_create(username=f"reviewer{number}")
        user.is_staff = False
        user.is_superuser = False
        user.set_password(password)
        user.save()
        if created:
            Document.objects.create(owner=user, title=f"Reviewer {number}: synthetic literature record", abstract="Fictional text for access-isolation testing only.", source="Synthetic demonstration")
print("Two non-administrator reviewer accounts are ready.")
