"""Validate the complete batch before performing transactional writes."""
import csv
import io
from django.core.exceptions import ValidationError
from django.db import transaction
from documents.models import Document

MAX_BYTES = 1024 * 1024
MAX_ROWS = 1000

def parse_csv(upload):
    raw = upload.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValidationError("The file exceeds 1 MiB. Split it into smaller files.")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError("Save the file as UTF-8 CSV and try again.") from exc
    if not text.strip():
        raise ValidationError("The file is empty. Add a header and at least one record.")
    if "\x00" in text:
        raise ValidationError("The file contains invalid null characters.")
    records = []
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValidationError("Column names must not be duplicated.")
        if not {"title", "abstract"}.issubset(headers):
            raise ValidationError("Required columns are title and abstract. Download the example CSV.")
        if set(headers) - {"title", "abstract", "source"}:
            raise ValidationError("Only title, abstract and source columns are supported.")
        for number, row in enumerate(reader, start=1):
            if number > MAX_ROWS:
                raise ValidationError("Use no more than 1,000 records per file.")
            if None in row or any(value is None for value in row.values()):
                raise ValidationError(f"Record {number}: column count does not match the header.")
            values = {key: value.strip() for key, value in row.items()}
            if not values["title"]:
                raise ValidationError(f"Record {number}: title is empty. Add a title.")
            if len(values["title"]) > 500:
                raise ValidationError(f"Record {number}: title exceeds 500 characters.")
            if len(values.get("source", "")) > 255:
                raise ValidationError(f"Record {number}: source exceeds 255 characters.")
            records.append(values)
    except csv.Error as exc:
        raise ValidationError("Malformed CSV. Check quoting and column separators.") from exc
    if not records:
        raise ValidationError("The file has a header but no records.")
    return records

def import_documents(upload, owner):
    records = parse_csv(upload)
    return save_records(records, owner)

def save_records(records, owner):
    # Owner comes from the authenticated request, never from a CSV column.
    with transaction.atomic():
        objects = [Document(owner=owner, **record) for record in records]
        for document in objects:
            document.full_clean()
        Document.objects.bulk_create(objects)
    return len(objects)
