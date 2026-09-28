from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from documents.models import Document

class PermissionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="alice")
        self.other = get_user_model().objects.create_user(username="bob")
        self.private = Document.objects.create(owner=self.other, title="Private record")

    def test_anonymous_redirects(self):
        for url in ["/", "/upload/", "/example.csv", f"/documents/{self.private.pk}/"]:
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_cross_user_isolation(self):
        self.client.force_login(self.user)
        self.assertNotContains(self.client.get("/"), "Private record")
        self.assertEqual(self.client.get(f"/documents/{self.private.pk}/").status_code, 404)

    def test_upload_owner_and_rendering(self):
        self.client.force_login(self.user)
        response = self.client.post("/upload/", {"file": SimpleUploadedFile("data.csv", b"title,abstract\n<script>alert(1)</script>,Text\n"), "owner": self.other.pk}, follow=True)
        doc = Document.objects.get(owner=self.user)
        self.assertContains(response, "Imported 1 document(s).")
        detail = self.client.get(reverse("documents:detail", args=[doc.pk]))
        self.assertContains(detail, "&lt;script&gt;")
        self.assertNotContains(detail, "<script>")

    def test_invalid_upload_shows_actionable_error(self):
        self.client.force_login(self.user)
        response = self.client.post("/upload/", {"file": SimpleUploadedFile("data.csv", b"title,abstract\n,Text\n")})
        self.assertContains(response, "Record 1: title is empty")
        self.assertEqual(Document.objects.filter(owner=self.user).count(), 0)

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post("/upload/", {}).status_code, 403)

    def test_pages_and_example(self):
        self.assertEqual(self.client.get("/accounts/login/").status_code, 200)
        self.client.force_login(self.user)
        self.assertContains(self.client.get("/upload/"), 'enctype="multipart/form-data"')
        self.assertEqual(self.client.get("/example.csv").status_code, 200)
        self.assertEqual(self.client.post("/accounts/logout/").status_code, 302)
