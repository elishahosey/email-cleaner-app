import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')

# Print statements to debug file paths
print("Base Directory:", BASE_DIR)
print("Credentials File Path:", CREDENTIALS_FILE)
print("Token File Path:", TOKEN_FILE)

def main():
  """Gather all emails and store 
  it into respective subjects
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  
  if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    
    
    if creds and creds.expired and creds.refresh_token:
          try:
              creds.refresh(Request())
          except RefreshError:   
            print("Failed to refresh token, re-authenticating...")
            flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
            creds = flow.run_local_server(port=8080)    
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          CREDENTIALS_FILE, SCOPES
      )
      creds = flow.run_local_server(port=8080)
      
      
    # Save the credentials for the next run
    with open(TOKEN_FILE, "w") as token:
      token.write(creds.to_json())
    

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    
    
    
    #gather list of each label of the user
    labels = fetch_user_labels(service)
    

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")
    
  return service

def fetch_emails_per_label(service, label_id):
  
   emails = []
   response = service.users().messages().list(userId='me', labelIds=[label_id]).execute()
   emails.extend(response.get('messages', [])) #adding result of response to email group

   #Too many emails
   while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId='me', labelIds=[label_id], pageToken=page_token).execute()
        emails.extend(response.get('messages', []))
   return emails

def get_email_length(emails):
  if len(emails) == 0:
    return 0
  else:
    return len(emails)
  

def fetch_user_labels(service):
  results = service.users().labels().list(userId="me").execute()
  labels = results.get("labels", [])
  
  if not labels:
      print("No labels found.")
      return None
  
  return labels

#labels + email length
def get_emailData(labels,service):
  label_emails = {}
    
    
  for label in labels:
    name = str(label["name"])
    emails = fetch_emails_per_label( service,label["id"])
    label_emails[name] = get_email_length(emails)
    
  return label_emails