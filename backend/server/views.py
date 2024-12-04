from django.shortcuts import render
from django.http import HttpResponse
import subprocess
from django.http import JsonResponse
from .runGmail.emailManage import main, fetch_user_labels, get_emailLengthForLabels, fetch_emails_per_label

# Create your views here.
#request -> response
#request handler

def run_gmail(request):
        try:
            #run the gmail API
            service = main()
            labels = fetch_user_labels(service)
            
            label_data = get_emailLengthForLabels(labels,service)
            
            #TODO: View content of emails and send it to postsgresql database
            email_data = getEmailData(service,label_data)
            
            return JsonResponse({"status": "success", "labels": label_data, "emails": email_data})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

      #TODOTest Format of email for Future ML project  && Find a way to list it in response

def getEmailData(service,label_data):
    labels = list(label_data.keys())
    emails = fetch_emails_per_label(service,labels[12])
    return emails
    