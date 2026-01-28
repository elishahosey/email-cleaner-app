import os
import pandas as pd
from backend.server.runGmail.emailManage import main as gmail_main,fetch_emails_per_label

def run_model():
    service = gmail_main() 
    response=fetch_emails_per_label(service, 'Label_2979067777648255447')
    print(response)
#TODO convert response to csv before data cleaning

if __name__ == "__main__":
    run_model()




