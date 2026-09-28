from django.urls import path
from . import views
app_name = "documents"
urlpatterns = [path("", views.document_list, name="list"), path("upload/", views.upload, name="upload"), path("example.csv", views.example_csv, name="example"), path("documents/<int:pk>/", views.document_detail, name="detail")]
