from django.urls import path
from .views import FileUploadView, ProcessFileView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('process/', ProcessFileView.as_view(), name='process-file'),
]
