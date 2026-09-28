from django import forms
from .services.import_csv import MAX_BYTES, parse_csv

class UploadForm(forms.Form):
    file = forms.FileField(
        label="CSV file",
        help_text="UTF-8 CSV, up to 1 MiB and 1,000 records. Required columns: title, abstract. Optional: source.",
        widget=forms.ClearableFileInput(attrs={"accept": ".csv"}),
    )

    def clean_file(self):
        upload = self.cleaned_data["file"]
        if not upload.name.lower().endswith(".csv"):
            raise forms.ValidationError("Choose a file with the .csv extension.")
        if upload.size > MAX_BYTES:
            raise forms.ValidationError("The file exceeds 1 MiB. Split it into smaller files.")
        self.records = parse_csv(upload)
        return upload
