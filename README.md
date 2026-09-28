# TCM Literature Import Sample

A small Django demonstration of actionable CSV validation and per-user literature records, inspired by the upload usability problem described for TCM Miner. This is newly written demonstration code, not the original TCM Miner implementation. It has no real users or clinical data.


## Local setup (Python 3.12 recommended)

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and sign in with the account you created. There are no embedded credentials. Upload `examples/valid.csv`, then try `examples/invalid.csv`. Use synthetic data only.

```sh
python manage.py test documents
python manage.py check
python manage.py makemigrations --check --dry-run
```

## Local Docker alternative

```sh
docker compose build
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py createsuperuser
docker compose up
```

A named volume preserves the SQLite database. The port is bound to localhost. This uses Django's development server and is a local review environment, not production deployment. Docker execution must be verified separately if Docker is unavailable on the development machine.

## Reviewer reading order

1. `documents/services/import_csv.py`: bounded parsing, actionable errors and atomic persistence.
2. `documents/views.py`: authenticated ownership filtering and upload workflow.
3. `documents/tests/test_import.py` and `test_permissions.py`: validation, rollback, ownership, CSRF and HTML escaping.
4. `documents/models.py` and `forms.py`: data contract and upload validation.

## Design decisions

- CSV schema: required `title` and `abstract` columns, optional `source`; abstract values may be empty. Unknown or duplicated headers are rejected. Titles are trimmed and required. UTF-8 with or without BOM is supported.
- Bounds: 1 MiB and 1,000 records per upload. Errors refer to logical record numbers, excluding the header; multiline fields can span physical lines.
- Validate all records first, then save within a transaction. Failed batches leave no partial imports. Tests simulate a failure after a write to check rollback.
- SQLite reduces reviewer setup. A multi-user production service would need separate capacity and database decisions.
- Ownership is assigned on the server; CSV cannot supply it. Detail requests for another user's record return 404. Even privileged accounts see only their own records in these views.
- Original uploaded files are not retained. Records are associated with the importer. Deleting an account cascades to its records; a preservation archive would require a different retention policy.
- Templates use escaping, CSRF protection, labels, text errors and native keyboard-operable controls. No formal accessibility conformance audit has been performed.

## Deliberate limitations

No NLP inference, file deduplication, background processing, REST API, registration or production hosting is included. Re-uploading a valid file creates additional records, as disclosed on the page. Application-level size checks occur after Django receives the request; a public deployment needs proxy request limits, abuse prevention, HTTPS, secret management and backups. Automated tests do not establish performance, accessibility certification or improvements in user retention.

## Application use

The original TCM platform's 105 registered users are background experience, not users of this demo. Do not transfer test or deployment claims from this new sample into descriptions of the original project. Read and review the implementation before submitting it; record any subsequent changes and explain AI assistance in the application.
