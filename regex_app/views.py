# regex_app/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import UploadedFile
import pandas as pd
import re

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.data['file']
        uploaded_file = UploadedFile.objects.create(file=file_obj)
        return Response({'file_id': uploaded_file.id}, status=status.HTTP_201_CREATED)

class ProcessFileView(APIView):

    def post(self, request, *args, **kwargs):
        file_id = request.data.get('file_id')
        pattern_description = request.data.get('pattern_description')
        replacement_value = request.data.get('replacement_value')
        
        # Dummy LLM for converting natural language to regex
        regex_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'
        
        uploaded_file = UploadedFile.objects.get(id=file_id)
        file_path = uploaded_file.file.path
        data = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
        
        for col in data.select_dtypes(include=[object]):
            data[col] = data[col].apply(lambda x: re.sub(regex_pattern, replacement_value, x) if isinstance(x, str) else x)
        
        response_data = data.to_dict(orient='records')
        return Response(response_data, status=status.HTTP_200_OK)
