from django.shortcuts import render
from django.http import HttpResponse
import json
import subprocess
from django.http import JsonResponse
from .runGmail.emailManage import main, fetch_user_labels, get_emailLengthForLabels, fetch_emails_per_label,delete_emails_by_label_keyword


def get_service():
    service = main()
    return service

def run_gmail(request):
        try:
            # Initialize the Gmail service
            service = get_service()
            labels = fetch_user_labels(service)
            
            label_data = get_emailLengthForLabels(labels,service)
            email_data = getEmailData(service,label_data)
            
            return JsonResponse({"status": "success", "labels": label_data, "emails": email_data})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


def getEmailData(service,label_data):
    labels = list(label_data.keys())
    emails = fetch_emails_per_label(service,labels[12])
    return emails


def fetchEmails(request):
    try:
        service = get_service()
       
        # req = json.loads(request.body)
        keyword = request.GET.get("keyword", "")
        sender = request.GET.get("sender", "")
        query = ""
        if keyword and sender:
            query = f'from:{sender} {keyword}'
        elif keyword:
            query = keyword
        elif sender:
            query = f'from:{sender}'
        
        emails = service.users().messages().list(userId='me', q={query}).execute()
        
        #log emails in a separate file for testing
        with open('./fetched_emails.json', 'w') as f:
            json.dump(emails, f, indent=4)
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

#TODO: Uncomment to delete emails
# def deleteEmail(request):
#     try:
#         service = get_service()
#         req = json.loads(request.body)
#         keyword = req.get("keyword", "")
#         delete_emails_by_label_keyword(service, keyword)
#         return JsonResponse({"status": "success", "message": "Email deleted successfully"})
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)
    