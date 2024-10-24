'''
Private Open Source License 1.0
Copyright 2024 Dominic Hord

https://github.com/DomTheDorito/Private-Open-Source-License

Permission is hereby granted, free of charge, to any person 
obtaining a copy of this software and associated documentation 
files (the “Software”), to deal in the Software without limitation 
the rights to personally use, copy, modify, distribute, and to 
permit persons to whom the Software is furnished to do so, subject 
to the following conditions:

1. The above copyright notice and this permission notice shall be 
included in all copies or substantial portions of the Software.

2. The source code shall not be used for commercial purposes, including 
but not limited to sale of the Software, or use in products intended for 
sale, unless express writen permission is given by the source creator.

3. Attribution to source work shall be made plainly available in a reasonable manner.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS 
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

THIS LICENSE MAY BE UPDATED OR REVISED, WITH NOTICE ON THE POS LICENSE REPOSITORY.
'''

from flask import Flask, render_template_string, send_file, request
import os
import glob
import re
import math

# Flask application
app = Flask(__name__)

# Backup directory where ADIF files are stored
BACKUP_DIR = './qrz_backups'

# Number of QSOs per page
QSOS_PER_PAGE = 10

# HTML template with search, pagination, sorting functionality, and QSO detail links
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ham Radio Logbook</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        th a {
            color: white;
            text-decoration: none;
        }
        th a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="my-4">Local Logger 1.0.0</h1>
        <p>Latest Backup: {{ latest_backup }}</p>

        <form method="get" action="/" class="my-3">
            <div class="input-group">
                <input type="text" name="query" class="form-control" placeholder="Search (call, frequency, mode, etc.)" value="{{ query }}">
                <button class="btn btn-primary" type="submit">Search</button>
            </div>
        </form>

        <table class="table table-striped">
            <thead class="table-dark">
                <tr>
                    <th><a href="/?sort_by=call&order={{ 'desc' if sort_by == 'call' and order == 'asc' else 'asc' }}&query={{ query }}&page={{ current_page }}">Call</a></th>
                    <th><a href="/?sort_by=freq&order={{ 'desc' if sort_by == 'freq' and order == 'asc' else 'asc' }}&query={{ query }}&page={{ current_page }}">Frequency</a></th>
                    <th><a href="/?sort_by=band&order={{ 'desc' if sort_by == 'band' and order == 'asc' else 'asc' }}&query={{ query }}&page={{ current_page }}">Band</a></th>
                    <th><a href="/?sort_by=mode&order={{ 'desc' if sort_by == 'mode' and order == 'asc' else 'asc' }}&query={{ query }}&page={{ current_page }}">Mode</a></th>
                    <th><a href="/?sort_by=qso_date&order={{ 'desc' if sort_by == 'qso_date' and order == 'asc' else 'asc' }}&query={{ query }}&page={{ current_page }}">Date</a></th>
                    <th><a href="/?sort_by=time_on&order={{ 'desc' if sort_by == 'time_on' and order == 'asc' else 'asc' }}&query={{ query }}&page={{ current_page }}">Time</a></th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                {% for entry in logbook_entries %}
                <tr>
                    <td>{{ entry['call'] }}</td>
                    <td>{{ entry['freq'] }}</td>
                    <td>{{ entry['band'] }}</td>
                    <td>{{ entry['mode'] }}</td>
                    <td>{{ entry['qso_date'] }}</td>
                    <td>{{ entry['time_on'] }}</td>
                    <td>
                        <a href="/qso/{{ entry['app_qrzlog_logid'] }}" class="btn btn-primary">View</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="d-flex justify-content-between align-items-center my-3">
            <a class="btn btn-secondary {% if current_page == 1 %}disabled{% endif %}" href="/?page={{ current_page - 1 }}&query={{ query }}&sort_by={{ sort_by }}&order={{ order }}">
                &laquo; Previous
            </a>

            <form class="d-flex align-items-center" method="get" action="/">
                <label for="pageInput" class="me-2">Page:</label>
                <input type="number" id="pageInput" name="page" value="{{ current_page }}" min="1" max="{{ total_pages }}" class="form-control me-2" style="width: 80px;">
                <input type="hidden" name="query" value="{{ query }}">
                <input type="hidden" name="sort_by" value="{{ sort_by }}">
                <input type="hidden" name="order" value="{{ order }}">
                <button type="submit" class="btn btn-primary">Go</button>
            </form>

            <a class="btn btn-secondary {% if current_page == total_pages %}disabled{% endif %}" href="/?page={{ current_page + 1 }}&query={{ query }}&sort_by={{ sort_by }}&order={{ order }}">
                Next &raquo;
            </a>
        </div>

        <br>
        <a href="/download" class="btn btn-primary">Download Latest Logbook</a>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# HTML template for QSO detail view
qso_detail_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QSO Details</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1 class="my-4">QSO Details</h1>
        <p><strong>Callsign:</strong> {{ entry['call'] }}</p>
        <p><strong>Name:</strong> {{ entry['name'] }}</p>
        <p><strong>DXCC Number:</strong> {{ entry['dxcc'] }}</p>
        <p><strong>State:</strong> {{ entry['state'] }}</p>
        <p><strong>Their Grid:</strong> {{ entry['gridsquare'] }}</p>
        <p><strong>My Grid:</strong> {{ entry['my_gridsquare'] }}</p>
        <p><strong>Their CQ Zone:</strong> {{ entry['cqz'] }}</p>
        <p><strong>Their ITU Zone:</strong> {{ entry['ituz'] }}</p>
        <p><strong>Transmit Frequency:</strong> {{ entry['freq'] }}</p>
        <p><strong>Receive Frequency:</strong> {{ entry['freq_rx'] }}</p>
        <p><strong>Mode:</strong> {{ entry['mode'] }}</p>
        <p><strong>Date:</strong> {{ entry['qso_date'] }}</p>
        <p><strong>Time:</strong> {{ entry['time_on'] }}</p>
        <p><strong>ESQL?:</strong> {{ entry['eqsl_qsl_rcvd'] }}</p>
        <p><strong>LOTW?:</strong> {{ entry['lotw_qsl_rcvd'] }}</p>
        <p><strong>QRZ?:</strong> {{ entry['qsl_rcvd'] }}</p>
        <p><strong>Satellite Name:</strong> {{ entry['sat_name'] }}</p>
        <p><strong>QSL Received:</strong> {{ entry['qsl_rcvd'] }}</p>
        <a href="/" class="btn btn-primary">Back to Logbook</a>
    </div>
</body>
</html>
"""

# Function to parse ADIF data into a list of dictionaries
def parse_adif(adif_data):
    entries = []
    qsos = adif_data.split('<eor>')

    for qso in qsos:
        entry = {}
        entry['call'] = re.search(r'<call:(\d+)>(\S+)', qso)
        entry['name'] = re.search(r'<name:(\d+)>(\S+)', qso)
        entry['dxcc'] = re.search(r'<dxcc:(\d+)>(\S+)', qso)
        entry['state'] = re.search(r'<state:(\d+)>(\S+)', qso)
        entry['gridsquare'] = re.search(r'<gridsquare:(\d+)>(\S+)', qso)
        entry['my_gridsquare'] = re.search(r'<my_gridsquare:(\d+)>(\S+)', qso)
        entry['cqz'] = re.search(r'<cqz:(\d+)>(\S+)', qso)
        entry['ituz'] = re.search(r'<ituz:(\d+)>(\S+)', qso)
        entry['freq'] = re.search(r'<freq:(\d+)>(\S+)', qso)
        entry['freq_rx'] = re.search(r'<freq_rx:(\d+)>(\S+)', qso)
        entry['band'] = re.search(r'<band:(\d+)>(\S+)', qso)
        entry['mode'] = re.search(r'<mode:(\d+)>(\S+)', qso)
        entry['qso_date'] = re.search(r'<qso_date:(\d+)>(\S+)', qso)
        entry['time_on'] = re.search(r'<time_on:(\d+)>(\S+)', qso)
        entry['eqsl_qsl_rcvd'] = re.search(r'<eqsl_qsl_rcvd:(\d+)>(\S+)', qso)
        entry['lotw_qsl_rcvd'] = re.search(r'<lotw_qsl_rcvd:(\d+)>(\S+)', qso)
        entry['qsl_rcvd'] = re.search(r'<qsl_rcvd:(\d+)>(\S+)', qso)
        entry['sat_name'] = re.search(r'<sat_name:(\d+)>(\S+)', qso)
        entry['app_qrzlog_logid'] = re.search(r'<app_qrzlog_logid:(\d+)>(\S+)', qso)

        for key in entry.keys():
            match = entry[key]
            entry[key] = match.group(2) if match else None

        # Ensure the call field is present and non-empty
        if entry['call']:
            entries.append(entry)

    return entries

# Function to get the latest backup file from the backup directory
def get_latest_backup():
    # List all files in the backup directory
    backup_files = glob.glob(os.path.join(BACKUP_DIR, '*.adif'))  # Assuming .adi files are the backups

    if not backup_files:
        return None

    # Sort the files by modification time, newest first
    latest_backup = max(backup_files, key=os.path.getmtime)
    
    return latest_backup

# Route to render the logbook with search, pagination, sorting functionality
@app.route('/')
def logbook():
    query = request.args.get('query', '')
    page = int(request.args.get('page', 1))
    sort_by = request.args.get('sort_by', 'call')
    order = request.args.get('order', 'asc')

    # Get the latest backup file
    latest_backup = get_latest_backup()

    if not latest_backup:
        return "No backup files found.", 404

    # Read the latest backup file and parse ADIF data
    with open(latest_backup, 'r') as f:
        adif_data = f.read()

    logbook_entries = parse_adif(adif_data)

    # Sort logbook entries by the specified field and order
    reverse = (order == 'desc')
    logbook_entries = sorted(logbook_entries, key=lambda x: x.get(sort_by, ''), reverse=reverse)

    # Filter logbook entries by query
    if query:
        logbook_entries = [entry for entry in logbook_entries if query.lower() in str(entry).lower()]

    # Pagination logic
    total_entries = len(logbook_entries)
    total_pages = math.ceil(total_entries / QSOS_PER_PAGE)
    logbook_entries = logbook_entries[(page - 1) * QSOS_PER_PAGE: page * QSOS_PER_PAGE]

    return render_template_string(html_template, latest_backup=os.path.basename(latest_backup),
                                  logbook_entries=logbook_entries, query=query,
                                  current_page=page, total_pages=total_pages,
                                  sort_by=sort_by, order=order)

# Route to display QSO details for a specific QSO based on APP_QRZLOG_LOGID
@app.route('/qso/<string:log_id>')
def qso_detail(log_id):
    latest_backup = get_latest_backup()

    if not latest_backup:
        return "No backup files found.", 404

    # Read the latest backup file and parse ADIF data
    with open(latest_backup, 'r') as f:
        adif_data = f.read()

    logbook_entries = parse_adif(adif_data)

    # Find the entry with the given APP_QRZLOG_LOGID
    entry = next((entry for entry in logbook_entries if entry['app_qrzlog_logid'] == log_id), None)

    if not entry:
        return "QSO not found.", 404

    return render_template_string(qso_detail_template, entry=entry)

# Route to download the latest logbook file
@app.route('/download')
def download():
    latest_backup = get_latest_backup()

    if not latest_backup:
        return "No backup files found.", 404

    return send_file(latest_backup, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
