from django.shortcuts import render
from django.http import HttpResponse
import json
import subprocess
from django.http import JsonResponse
from .runGmail.emailManage import *
#from .runGmail.emailManage import main, fetch_user_labels, get_emailLengthForLabels, fetch_emails_per_label,move_emails_to_label,delete_emails_by_label_keyword


def get_service():
    service = main()
    return service

def run_gmail(request):
        try:
            
            # Initialize the Gmail service
            service = get_service()
            labels = fetch_user_labels(service)
            
            #TODO: make this optional if no cache_labels json file doesn't exist
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
        
        # grab one block from this path
        fetchedEmailPath = '../backend/fetched_emails.json'
        json_fetched_emails = json.load(open(fetchedEmailPath))
        msg = json_fetched_emails['messages']
        # # print(email_data)
        
        service = get_service()
        #formatting my request for GMail API
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
        
        #referencing specific emails from GMail API
        requested_emails = service.users().messages().list(userId='me', q={query}).execute()
        
        
        #move fetched emails to a training for ML
        label_name=''
         
        move_emails_to_label(service,msg,label_name)
        # #log emails in a separate file for testing
        # with open('./fetched_emails.json', 'w') as f:
        #     json.dump(emails, f, indent=4)
        return JsonResponse({"status": "success"}, filteredEmails=requested_emails)
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
    