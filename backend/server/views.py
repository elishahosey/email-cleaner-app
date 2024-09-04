from django.shortcuts import render
from django.http import HttpResponse
import subprocess
from django.http import JsonResponse
from .runGmail.emailManage import main

# Create your views here.
#request -> response
#request handler

def run_gmail(request):
        try:
            result = main()
            return JsonResponse({"status": "success", "output": result.stdout})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)