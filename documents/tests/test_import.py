import io
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from documents.forms import UploadForm
from documents.models import Document
from documents.services.import_csv import import_documents, parse_csv, MAX_BYTES

class ImportTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="researcher")

    def test_unicode_and_optional_fields(self):
        count = import_documents(io.BytesIO("\ufefftitle,abstract\n中医研究,\n".encode()), self.user)
        self.assertEqual(count, 1)
        self.assertEqual(Document.objects.get().title, "中医研究")
        self.assertEqual(Document.objects.get().owner, self.user)

    def test_invalid_inputs(self):
        cases = [b"", b"title,abstract\n", b"title\nA\n", b"title,title,abstract\nA,B,C\n", b"title,abstract,owner\nA,B,1\n", b"title,abstract\nA\n", b"title,abstract\nA,B,C\n", b"title,abstract\n ,B\n", b"\xff", b"title,abstract\nA,\x00\n", b'title,abstract\nA,"unclosed', ("title,abstract\n" + "x"*501 + ",B\n").encode(), ("title,abstract,source\nA,B," + "x"*256).encode(), b"x"*(MAX_BYTES+1), b"title,abstract\n"+b"A,B\n"*1001]
        for data in cases:
            with self.subTest(data=data[:40]):
                with self.assertRaises(ValidationError):
                    parse_csv(io.BytesIO(data))

    def test_late_error_saves_nothing(self):
        with self.assertRaises(ValidationError):
            import_documents(io.BytesIO(b"title,abstract\nValid,B\n,B\n"), self.user)
        self.assertEqual(Document.objects.count(), 0)

    def test_database_failure_rolls_back(self):
        def partial_write(objects):
            objects[0].save()
            raise RuntimeError("Simulated database failure")
        with patch("documents.services.import_csv.Document.objects.bulk_create", side_effect=partial_write):
            with self.assertRaises(RuntimeError):
                import_documents(io.BytesIO(b"title,abstract\nA,B\nC,D\n"), self.user)
        self.assertEqual(Document.objects.count(), 0)

    def test_file_extension(self):
        form = UploadForm(files={"file": SimpleUploadedFile("data.txt", b"title,abstract\nA,B\n")})
        self.assertFalse(form.is_valid())
        self.assertIn(".csv", str(form.errors))

    def test_form_size_limit(self):
        form = UploadForm(files={"file": SimpleUploadedFile("data.csv", b"x"*(MAX_BYTES+1))})
        self.assertFalse(form.is_valid())
        self.assertIn("1 MiB", str(form.errors))
