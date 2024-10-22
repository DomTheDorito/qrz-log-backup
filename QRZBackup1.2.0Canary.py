
# Private Open Source License 1.0
# Copyright 2024 Dominic Hord
#
# https://github.com/DomTheDorito/Private-Open-Source-License
#
# Permission is hereby granted, free of charge, to any person obtaining 
# a copy of this software and associated documentation files (the “Software”), 
# to deal in the Software without limitation the rights to personally use, 
# copy, modify, distribute, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# 1. The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# 2. The source code shall not be used for commercial purposes, including but not 
# limited to sale of the Software, or use in products intended for sale, unless 
# express writen permission is given by the source creator.
#
# 3. Attribution to source work shall be made plainly available in a reasonable manner.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.
#
# THIS LICENSE MAY BE UPDATED OR REVISED, WITH NOTICE ON THE POS LICENSE REPOSITORY.


import requests
import os
from datetime import datetime
import glob
import html  # To decode HTML entities
import msal
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# QRZ API key
QRZ_API_KEY = 'your_api_key'

# Backup settings
BACKUP_DIR = './qrz_backups'
BACKUP_COUNT = 7
ADIF_FILENAME = 'qrz_logbook_backup_{timestamp}.adif'

# QRZ API URL for fetching logbook in ADIF format
QRZ_LOGBOOK_ADIF_URL = f"https://logbook.qrz.com/api?key={QRZ_API_KEY}&action=fetch&option=adif"

# Custom application header
HEADERS = {
    'User-Agent': 'QRZLogBackup/1.2.0'
}
'''
# Google Drive configuration
CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
'''

'''
# OneDrive configuration
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
AUTHORITY = 'https://login.microsoftonline.com/common'
ONEDRIVE_SCOPES = ['Files.ReadWrite.All']
REDIRECT_URI = 'http://localhost'
'''
# Fetch logbook data in ADIF format using API key
def fetch_logbook_adif():
    response = requests.get(QRZ_LOGBOOK_ADIF_URL, headers=HEADERS)
    if response.status_code == 200:
        if 'STATUS=FAIL' in response.text:
            raise Exception(f"QRZ API failed: {response.text}")
        
        # Decode the HTML entities
        decoded_data = html.unescape(response.text)
        return decoded_data  # Return decoded ADIF data
    else:
        raise Exception(f"Failed to fetch logbook from QRZ API, status code: {response.status_code}")

# Save logbook data to ADIF file
def save_logbook_data(logbook_data):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    adif_file = os.path.join(BACKUP_DIR, ADIF_FILENAME.format(timestamp=timestamp))
    
    # Write the decoded data to the ADIF file
    with open(adif_file, 'w') as f:
        f.write(logbook_data)
    
    print(f"Backup saved: {adif_file}")
    return adif_file

# Manage backups, keep only the 7 most recent
def manage_backups():
    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, '*.adif')))
    
    # If more than BACKUP_COUNT backups exist, remove the oldest ones
    if len(backups) > BACKUP_COUNT:
        for old_backup in backups[:-BACKUP_COUNT]:
            os.remove(old_backup)
            print(f"Deleted old backup: {old_backup}")
'''
# Google Drive authentication and upload
def authenticate_google_drive():
    """Authenticate and create a Google Drive service instance."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def upload_to_google_drive(file_path):
    """Uploads a file to Google Drive."""
    service = authenticate_google_drive()
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File uploaded to Google Drive with ID: {file.get('id')}")
'''

'''
# OneDrive authentication and upload
def authenticate_onedrive():
    """Authenticate and get an access token for OneDrive."""
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    
    # Attempt to acquire a token from cache
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(ONEDRIVE_SCOPES, account=accounts[0])
    else:
        # Interactive login for the first time
        flow = app.initiate_device_flow(scopes=ONEDRIVE_SCOPES)
        print(flow['message'])  # This provides the code to log in via browser
        result = app.acquire_token_by_device_flow(flow)

    if 'access_token' in result:
        return result['access_token']
    else:
        raise Exception("Failed to authenticate OneDrive.")

def upload_to_onedrive(file_path):
    """Uploads a file to OneDrive."""
    access_token = authenticate_onedrive()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream'
    }

    # OneDrive upload endpoint
    upload_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/backups/{os.path.basename(file_path)}:/content'

    with open(file_path, 'rb') as f:
        response = requests.put(upload_url, headers=headers, data=f)
    
    if response.status_code == 201:
        print(f"File uploaded to OneDrive: {response.json()['name']}")
    else:
        print(f"Failed to upload file to OneDrive: {response.text}")
'''
# Main function to run the backup process
def run_backup():
    try:
        # Ensure backup directory exists
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        # Fetch logbook in ADIF format using API key
        logbook_data = fetch_logbook_adif()
        
        # Save logbook data to ADIF file
        adif_file = save_logbook_data(logbook_data)
        
        # Manage backups
        manage_backups()
'''
        # Upload the backup to Google Drive
        run_google_drive_backup(adif_file)
'''

''' 
        # Upload the backup to OneDrive
        run_onedrive_backup(adif_file)
'''
    except Exception as e:
        print(f"Error: {e}")

# Schedule this script to run nightly (via cron or task scheduler)
if __name__ == '__main__':
    run_backup()
