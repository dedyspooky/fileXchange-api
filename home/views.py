from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FileListSerializer
from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Folder
from django.core.files import File
import os
import zipfile
from django.conf import settings

class HandleFileUpload(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            data = request.data
            # Check if the 'file' key is present in the request data
            if 'file' not in data:
                return Response({
                    'status': 'error',
                    'message': 'File not provided in the request',
                }, status=400)

            serializer = FileListSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'File is ready to share.',
                    'data': serializer.data
                })
            return Response({
                'status': 'error',
                'message': 'Something went wrong',
                'data': serializer.errors
            })
        except Exception as e:
            print("Error in file upload view", str(e))
            return Response({
                'status': 'error',
                'message': 'Internal server error',
            }, status=500)


from rest_framework import status

class HandleFileDownload(APIView):
    # ...

    def get(self, request, uid):
        folder = get_object_or_404(Folder, uid=uid)
        zip_file_path = os.path.join(settings.MEDIA_ROOT, 'zip', f'{uid}.zip')

        if not os.path.exists(zip_file_path):
            folder_files = folder.files_set.all()
            if not folder_files:
                return Response({
                    'status': 'error',
                    'message': 'No files found in the folder',
                }, status=status.HTTP_404_NOT_FOUND)

            self.zip_files(folder_files, zip_file_path)

        return FileResponse(open(zip_file_path, 'rb'), as_attachment=True)
