import os
import pandas as pd
from backend.server.runGmail.emailManage import main,fetch_emails_per_label
  
service = main() #Initialize Gmail service
response=fetch_emails_per_label(service, 'Label_2979067777648255447')

#TODO convert response to csv before data cleaning




