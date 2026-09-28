"""Literature records for the TCM import demonstration.

Written with AI assistance using the Django official documentation patterns:
https://docs.djangoproject.com/en/5.2/topics/db/models/
https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#referencing-the-user-model

This is a new demonstration, not an extract from the original TCM Miner code.
Ownership records do not enforce access control; views must filter by user.
"""

from django.conf import settings
from django.db import models


class Document(models.Model):
    """A literature record imported by a user."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    title = models.CharField(max_length=500)
    abstract = models.TextField(blank=True)
    source = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return self.title
