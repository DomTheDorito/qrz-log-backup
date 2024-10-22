# QRZ Log Backup
Simple program that backs up your entire QRZ Log.

After the LoTW fiasco in May, being able to have a local backup is invaluable, as no one
knew if their logs were gone or not.

Written in Python, this program backs up your entire log from QRZ, so long as you have an 
active XML subscription.

The program is set by default to keep the 7 most recent log files, as the intent is to run this nightly 
via a cronjob or if on Windows, task scheduler, and keepa weeks worth of backups. The amount of backups
can easily be changed in the "BACKUP_COUNT" variable.
