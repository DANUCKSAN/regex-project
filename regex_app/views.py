import pandas as pd
import re
import requests
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UploadedFile
from .serializers import UploadedFileSerializer

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = UploadedFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'file_id': serializer.data['id']}, status=201)
        return Response(serializer.errors, status=400)

class ProcessFileView(APIView):
    def post(self, request, *args, **kwargs):
        file_id = request.data.get('file_id')
        pattern_desc = request.data.get('pattern_desc')
        replacement = request.data.get('replacement')

        try:
            uploaded_file = UploadedFile.objects.get(id=file_id)
            file_path = uploaded_file.file.path

            # Convert natural language to regex
            regex_pattern = self.convert_to_regex(pattern_desc)

            # Process the file
            data = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)
            for column in data.select_dtypes(include=['object']).columns:
                data[column] = data[column].astype(str).replace(regex_pattern, replacement, regex=True)

            # Save the processed file
            processed_file_path = file_path.replace('uploads', 'processed')
            data.to_csv(processed_file_path, index=False)

            return JsonResponse({'message': 'File processed successfully', 'file_path': processed_file_path})

        except UploadedFile.DoesNotExist:
            return JsonResponse({'error': 'File not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def convert_to_regex(self, description):
        # Dummy LLM API call for regex conversion
        # Replace with actual LLM integration
        response = requests.post('https://api.llm.example/convert_to_regex', json={'description': description})
        if response.status_code == 200:
            return response.json().get('regex_pattern', '')
        return ''
