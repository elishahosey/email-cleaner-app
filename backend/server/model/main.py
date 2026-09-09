import base64
import csv
from server.runGmail.emailManage import main as gmail_main, fetch_emails_per_label,gather_email_data

def decrypt_email_body(email_data):
    try:
        payload = email_data.get('payload', {})
        body = payload.get('body', {})
        data = body.get('data', '')

        if data:
            decoded_data = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode('utf-8')
            return decoded_data
        else:
            return ""
    except Exception as e:
        print(f"Error decoding email body: {e}")
        return ""

def preprocess_email_data(email_data):
   #headers of inerest: Snippet,headers(Delivered-To, Received,From,Reply-To,To,Subject,Content-Type,Date)
    preprocessed_data = {
        'id': email_data.get('id', ''),
        'threadId': email_data.get('threadId', ''),
        'snippet': email_data.get('snippet', ''),
        # Add more fields as necessary
    }
    return preprocessed_data

def create_csv_from_emails(emails, output_path="emails.csv"):
    if not emails:
        return output_path
    with open(output_path, "w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=emails[0].keys())
        writer.writeheader()
        writer.writerows(emails)
    return output_path

#TODO:create model
# #def run_model():


#TODO convert response to csv before data cleaning

#email_csv =

if __name__ == "__main__":
    service = gmail_main()
    response=fetch_emails_per_label(service, 'Label_2979067777648255447') #returns id, threadId of each email in the label
    email_csv = []
    for email in response:
        email_data = gather_email_data(service, email['id'])
        preprocessed_data = preprocess_email_data(email_data)
        email_csv.append(preprocessed_data)

    create_csv_from_emails(email_csv)




