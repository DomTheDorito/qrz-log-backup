
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

# QRZ API key
QRZ_API_KEY = 'your-qrz-api-key'

# Backup settings
BACKUP_DIR = './qrz_backups'
BACKUP_COUNT = 7
ADIF_FILENAME = 'qrz_logbook_backup_{timestamp}.adif'

# QRZ API URL for fetching logbook in ADIF format
QRZ_LOGBOOK_ADIF_URL = f"https://logbook.qrz.com/api?key={QRZ_API_KEY}&action=fetch&option=ALL"

# Custom application header
HEADERS = {
    'User-Agent': 'QRZLogBackup/1.0.1'
}

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
    with open(adif_file, 'w', encoding='utf-8') as f:
        f.write(logbook_data)
    
    print(f"Backup saved: {adif_file}")
    return adif_file

# Manage backups, keep only the 7 most recent
def manage_backups():
    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, '*.adif')), key=os.path.getctime)
    
    # If more than BACKUP_COUNT backups exist, remove the oldest ones
    if len(backups) > BACKUP_COUNT:
        for old_backup in backups[:-BACKUP_COUNT]:
            os.remove(old_backup)
            print(f"Deleted old backup: {old_backup}")

# Main function to run the backup process
def run_backup():
    try:
        # Ensure backup directory exists
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        # Fetch logbook in ADIF format using API key
        logbook_data = fetch_logbook_adif()
        
        # Save logbook data to ADIF file
        save_logbook_data(logbook_data)
        
        # Manage backups
        manage_backups()

    except Exception as e:
        print(f"Error: {e}")

# Schedule this script to run nightly (via cron or task scheduler)
if __name__ == '__main__':
    run_backup()
