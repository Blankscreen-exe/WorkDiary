import argparse
import csv
import sqlite3
from datetime import datetime
import os
from colors import colors as col
from settings import settings as setting

DB_FILE = setting['db_dir']


def create_database():
    conn = sqlite3.connect(DB_FILE)
    curr = conn.cursor()
    curr.execute('CREATE TABLE IF NOT EXISTS work_log (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, date DATE, time TEXT)')
    conn.commit()
    conn.close()

def status_today():
    today = datetime.today().strftime('%d-%m-%Y')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT COUNT(id) FROM work_log WHERE date = ?',(today,))
    count = c.fetchone()[0]
    conn.close()
    
    print(f'{col.fg.pink}Number of logs today({today}) => {col.bold + col.fg.lightgreen + str(count) + col.reset}')

def log_work():
    
    print("="*30)
    print('\033[1;36;40m'+" "*5+'Welcome to your Logs'+" "*5+"\033[0m")
    print("="*30)
    
    while True:
        print(f"""
\033[43;31;1m 1 {col.reset} - log entry
\033[43;31;1m 2 {col.reset} - list today's logs
\033[43;31;1m 3 {col.reset} - check status
\033[43;31;1m 4 {col.reset} - exit
              """)
        try:
            selection = eval(input(">> "))
        except:
            selection = None
        
        # logs entry
        if selection == 1 and isinstance(selection,int):
            name = input('{}Task name:{} '.format(col.bg.blue,col.reset))
            desc = input('{}Description:{} '.format(col.bg.blue,col.reset))
            date = datetime.now().strftime('%d-%m-%Y')
            time = datetime.now().strftime('%H:%M:%S')
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('INSERT INTO work_log (name, description, date, time) VALUES (?, ?, ?, ?)', (name, desc, date, time))
            conn.commit()
            conn.close()
            print(col.bold + col.fg.green + '💾 Work logged successfully @{} {}'.format(date, time) + col.reset)
        # list todays logs
        elif selection == 2 and isinstance(selection,int):
            timestamp = datetime.today().strftime('%d-%m-%Y')
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT id, name, description, date, time FROM work_log WHERE date = ?', (timestamp,))

            rows = c.fetchall()
            conn.close()
            
            print("="*30)
            print('\033[1;36;40m'+" "*1+f'📜 Log Entries of {timestamp}'+" "*1+"\033[0m")
            print("="*30)
            for record in rows:
                print(f"{col.bg.lightgrey+col.fg.black+col.bold}RECORD ID:  {col.reset} {record[0]} {col.bg.lightgrey+col.fg.black+col.bold}TIME:{col.reset} {record[4]}")
                print(f"{col.bg.lightgrey+col.fg.black+col.bold}TITLE:      {col.reset} {record[1]}")
                print(f"{col.bg.lightgrey+col.fg.black+col.bold}DESCRIPTION:{col.reset} {record[2]}")
                print("-"*30)
        # show today's status
        elif selection == 3 and isinstance(selection, int):
            status_today()
        # exit the program
        elif selection == 4 and isinstance(selection, int):
            break
        # default
        else:
            print('\033[1;31;40m'+'❌ INVALID RESPONSE: select an option from the menu'+'\033[0m')
    

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
    print(col.bold + col.fg.green + '🖨 Work log exported successfully' + col.reset)

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
    print(col.bold + col.fg.green + '🖨 Work log for date {} exported successfully.'.format(date) + col.reset)

if __name__ == '__main__':
    create_database()

    parser = argparse.ArgumentParser(
        description= col.bold + col.fg.blue + '{}'.format(setting['tool_description']) + col.reset,
        formatter_class=argparse.RawTextHelpFormatter
        )
    choices = ['log', 'export-all', 'export-date', 'status']
    parser.add_argument(
        'action', 
        nargs='?', 
        default='log', 
        choices=choices, 
        help=
"""
{} log {}           to add a work log
{} export-all {}    to export all work logs
{} export-date {}   to export work logs for a specific date
{} status {}        get current day status
""".format(*[col.bold+col.bg.cyan if i%2==0 else col.reset for i in range(len(choices)*2)])
            )
    parser.add_argument('-d', '--date', dest='date', help='🗓 Date to export {} (dd-mm-yyyy) {}'.format(col.bg.orange, col.reset))

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
    elif args.action == 'status':
        status_today()
    else:
        print('Error: unrecognized action')
        parser.print_usage()
        exit(1)

