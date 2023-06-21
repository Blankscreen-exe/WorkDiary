import os
import json
import csv
import sqlite3
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class work_diary:
    
    def __init__(self):
        # database settings
        self.db_filename = 'log_test.db'
        self.db_filepath = os.path.join('.')
        
        # database config
        self.query_type_const = {
            "all": "all",
            "today": "today",
            "sp_date": "sp_date",
            "id": "id",
        }
        
        # create database if not exists
        self.create_database()
        
        # export/import settings
        self.export_filename_prefix = 'work_log-'
        self.export_filename_suffix = ''
        self.export_filepath = os.path.join('.', 'exports')
        
        # smtp server 
        self.smtp_server = 'smtp.gmail.com'  # TODO: Update with the appropriate SMTP server
        
    # ===============================================================
    # ====================== Database Queries =======================
    # ===============================================================
        
    def create_database(self):
        # create directories if not exists
        if not os.path.exists(self.db_filepath):
            os.makedirs(self.db_filepath)
                
        conn = sqlite3.connect(os.path.join(self.db_filepath, self.db_filename))
        curr = conn.cursor()
        curr.execute('''CREATE TABLE IF NOT EXISTS work_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            scope TEXT, 
            context TEXT, 
            description TEXT, 
            tags TEXT, 
            date DATE, 
            time TEXT)
            ''')
        conn.commit()
        conn.close()    
        
    def get_records(self, query_type="all", id=None, date=None):
        """fetches records from the database base on the `query_type` param.
        """
        today_date = datetime.today().strftime('%d-%m-%Y')
        
        conn = sqlite3.connect(os.path.join(self.db_filepath, self.db_filename))
        c = conn.cursor()

        if query_type == self.query_type_const["all"]:
            c.execute('SELECT id, name, scope, context, description, tags, date, time FROM work_log')
        elif query_type == self.query_type_const["today"]:
            c.execute('SELECT id, name, scope, context, description, tags, date, time FROM work_log WHERE date = ?', (today_date,))
        elif query_type == self.query_type_const["sp_date"] and date is not None and not isinstance(date, tuple):
            c.execute('SELECT id, name, scope, context, description, tags, date, time FROM work_log WHERE date = ?', (date,))
        elif query_type == self.query_type_const["sp_date"] and date is not None and isinstance(date, tuple):
            c.execute('SELECT id, name, scope, context, description, tags, date, time FROM work_log WHERE date BETWEEN ? AND ?', (date[0], date[1],))
        elif query_type == self.query_type_const["id"] and id is not None:
            c.execute('SELECT id, name, scope, context, description, tags, date, time FROM work_log WHERE id = ?', (id,))
        # TODO: add get by date range
        else:
            raise AttributeError
        
        rows = c.fetchall()
        
        conn.close()
        
        return rows
    
    def update_record(self, id, data):
        # Connect to the database
        conn = sqlite3.connect(os.path.join(self.db_filepath, self.db_filename))
        cursor = conn.cursor()

        # Update the record
        set_values = ', '.join(f'{key} = ?' for key in data.keys())
        query = f"UPDATE work_log SET {set_values} WHERE id = ?"""
        cursor.execute(query, tuple(data.values()) + (id,))
        conn.commit()

        # Close the database connection
        conn.close()
    
    def insert_record(self, name, scope, context, description, tags):
        """inserts a log into the database
        """
        today_date = datetime.today().strftime('%d-%m-%Y')
        today_time = datetime.today().strftime('%H:%M') 
        # TODO: make variables for insert elements
        conn = sqlite3.connect(os.path.join(self.db_filepath, self.db_filename))
        c = conn.cursor()
        c.execute('''INSERT INTO work_log (
            name, 
            scope,
            context,
            description,
            tags, 
            date, 
            time
            ) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
            (name, scope, context, description, tags, today_date, today_time))
        conn.commit()
        conn.close()
        
    def delete_record(self, id):
        # Connect to the database
        conn = sqlite3.connect(os.path.join(self.db_filepath, self.db_filename))
        cursor = conn.cursor()

        # Delete the record
        cursor.execute("""DELETE FROM work_log WHERE id = ?""", (id,))
        conn.commit()

        # Close the database connection
        conn.close()
    
    def get_log_count(self, query_type="all", date=None):
        """gets count of logs based on `query_type` param
        """
        today_date = datetime.today().strftime('%d-%m-%Y')
        
        conn = sqlite3.connect(os.path.join(self.db_filepath, self.db_filename))
        c = conn.cursor()
        
        if query_type == self.query_type_const["all"]:
            c.execute('SELECT COUNT(id) FROM work_log')
            count = c.fetchone()[0]
        elif query_type == self.query_type_const["today"]:
            c.execute('SELECT COUNT(id) FROM work_log WHERE date = ?',(today_date,))
            count = c.fetchone()[0]
        elif query_type == self.query_type_const["sp_date"] and date is not None:
            c.execute('SELECT COUNT(id) FROM work_log WHERE date = ?',(date,))
            count = c.fetchone()[0]
        else:
            raise AttributeError
            
        conn.close()
        
        return count
    
    # ===============================================================
    # ======================== Export/Import ========================
    # ===============================================================

    def export_csv(self, query_type="all", date=None):

        conn = sqlite3.connect(os.path.join(self.db_filepath, self.db_filename))
        c = conn.cursor()
        
        if query_type == self.query_type_const["all"]:
            result = self.get_records()            
        elif query_type == self.query_type_const["today"]:
            result = self.get_records(query_type=self.query_type_const["today"])            
        elif query_type == self.query_type_const["sp_date"] and date is not None:
            result = self.get_records(query_type=self.query_type_const["sp_date"], date=date)            
        # TODO: add export by date range
        else:  
            raise AttributeError
        
        # create directories if not exists
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # write to file
        with open(os.path.join(export_dir, self.all_records_file_name), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['ID', 'Name', 'Scope', 'Context', 'Description', 'Tags', 'Date', 'Time'])
            for row in result:
                writer.writerow(row)
        
    # ===============================================================
    # ========================== Send Email =========================
    # ===============================================================

    def send_email(self, sender_email, sender_password, receiver_email, subject, message, attachment_path):

        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach the message to the email
        msg.attach(MIMEText(message, 'plain'))

        # Open the file in bynary
        with open(attachment_path, 'rb') as attachment:
            # Add file as application/octet-stream
            # Email clients will usually recognize this as an attachment
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {attachment_path}'
        )

        # Add attachment to message and convert message to string
        msg.attach(part)
        text = msg.as_string()

        # Send the email
        try:
            with smtplib.SMTP(self.smtp_server, 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, text)
        except smtplib.SMTPException as error:
            raise smtplib.SMTPException