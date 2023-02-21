import argparse
import csv
import sqlite3
from datetime import datetime
import os
from settings import settings as setting

DB_FILE = setting['db_dir']

def create_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS work_log (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, date DATE, time TEXT)')
    conn.commit()
    conn.close()

def log_work():
    name = input('Task name: ')
    desc = input('Description: ')
    date = datetime.now().strftime('%d-%m-%Y')
    time = datetime.now().strftime('%H:%M:%S')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO work_log (name, description, date, time) VALUES (?, ?, ?, ?)', (name, desc, date, time))
    conn.commit()
    conn.close()
    print('Work logged successfully.')

def export_all():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, name, description, date, time FROM work_log')
    rows = c.fetchall()
    conn.close()

    if not os.path.exists(setting['csv_dir']):
        os.makedirs(setting['csv_dir'])

    with open(os.path.join(setting['csv_dir'],setting['all_records_file_name']), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['ID', 'Name', 'Description', 'Date', 'Time'])
        for row in rows:
            writer.writerow(row)
    print('Work log exported successfully.')

def export_by_date(date):
    timestamp = datetime.strptime(date, '%d-%m-%Y').strftime('%d-%m-%Y')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, name, description, date, time FROM work_log WHERE date = ?', (timestamp,))

    rows = c.fetchall()
    conn.close()

    if not os.path.exists('logs'):
        os.makedirs('logs')

    with open(os.path.join(setting['csv_dir'],'{}{}.csv').format(setting['datewise_records_prefix'],date), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['ID', 'Name', 'Description', 'Date', 'Time'])
        for row in rows:
            writer.writerow(row)
    print('Work log for date {} exported successfully.'.format(date))

if __name__ == '__main__':
    create_database()

    parser = argparse.ArgumentParser(description='Work log')
    parser.add_argument('action', choices=['log', 'export-all', 'export-date'], help='Action to perform')
    parser.add_argument('--date', help='Date to export (dd-mm-yyyy)')

    args = parser.parse_args()

    if args.action == 'log':
        log_work()
    elif args.action == 'export-all':
        export_all()
    elif args.action == 'export-date':
        if not args.date:
            print('Error: date not specified.')
            parser.print_usage()
            exit(1)
        export_by_date(args.date)
