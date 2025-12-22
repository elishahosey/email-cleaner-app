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
            email_data = getEmailData(service)
            senders=grabSubscribersFromEmails(service)

           
            
            return JsonResponse({"status": "success", "labels": label_data, "emails": email_data,"senders":senders})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


def getEmailData(service):
    cache_path="./cached_labels.json"
    # Load cached label objects [{id, name, ...}]
    with open(cache_path, "r", encoding="utf-8") as f:
        cached_labels = json.load(f)

    emails_by_label = {}

    for lbl in cached_labels:
        label_name = lbl.get("name")
        label_id = lbl.get("id")

        if not isinstance(label_id, str) or not label_id.strip():
            print(f"[SKIP] Invalid label id for {label_name}: {label_id!r}")
            continue

        try:
            emails_by_label[label_name] = fetch_emails_per_label(
                service, label_id.strip()
            )
        except Exception as e:
            print(f"[FAIL] {label_name} ({label_id}): {e}")
            continue

    return emails_by_label


#collect distinct message IDs from multiple labels
def collect_message_ids(service, label_ids):
    all_ids = []

    for label_id in label_ids:
        response = service.users().messages().list(
            userId='me',
            labelIds=[label_id['id']]
        ).execute()

        ids = [msg['id'] for msg in response.get('messages', [])]
        all_ids.extend(ids)

    print("Collected Message IDs: ")
    return all_ids

def get_email_senders(service, msg_id):
    sender = []
    for i in msg_id:
        message = service.users().messages().get(userId='me', id=i, format='metadata', metadataHeaders=['From']).execute()
        headers = message.get('payload', {}).get('headers', [])    
        for header in headers:
            if header['name'] == 'From':
                s = header['value']
                sender.append(s)
    print("Collected Senders: ")
    final_senders = list(set(sender))
    return final_senders

#grab subscribers from collected messages
def grabSubscribersFromEmails(service):
    cached_labels_path = '../backend/cache_labels.json'
    with open(cached_labels_path, 'r') as f:
        cached_labels = json.load(f)
    
    
    msgIds = collect_message_ids(service, cached_labels)
    collect_senders = get_email_senders(service, msgIds)
    
    print("Final Collected Senders: ")
    return collect_senders


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
         
        move_emails_to_label(service,msg)
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
    