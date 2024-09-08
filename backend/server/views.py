from django.shortcuts import render
from django.http import HttpResponse
import subprocess
from django.http import JsonResponse
from .runGmail.emailManage import main, fetch_user_labels, get_emailData

# Create your views here.
#request -> response
#request handler

def run_gmail(request):
        try:
            #run the gmail API
            service = main()
            labels = fetch_user_labels(service)
            
            label_data = get_emailData(labels,service)
            
            
            return JsonResponse({"status": "success", "labels": label_data})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)