import PySimpleGUI as sg
import os
import json
import csv
import sqlite3
from datetime import datetime

DB_FILE = 'logs.db'
class work_diary():
    """
    This class represents an app that allows users to register and view quick launch shortcuts.
    """

    def __init__(self):
        # app settings
        self.app_theme = "Reddit"
        sg.theme(self.app_theme)
        self.app_icon = "./book.ico"
        self.window_size = (300, 220)
        self.section_title_font = ("Arial Rounded", 17)
        self.section_normal_font = ("MS Sans Serif", 10)
        self.window = sg.Window(
                                "Work Diary",
                                self.main_layout(), 
                                icon=self.app_icon
                                )
        
        # create table if not exists
        self.create_database()
        
        # database config
        self.today = datetime.today().strftime('%d-%m-%Y')
        self.query_type_const = {
            "all": "all",
            "today": "today",
            "sp_date": "sp_date",
        }
        
        # export/import config
        self.export_dir = "logs"
        self.all_records_file_name = 'all_export.csv'

    # ===============================================================
    # ======================== Data Queries =========================
    # ===============================================================
    
    def create_database(self):
        conn = sqlite3.connect(DB_FILE)
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
    
    def get_records(self, query_type="all", date=None):
        """fetches records from the database base on the `query_type` param.
        """
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        if query_type == self.query_type_const["all"]:
            c.execute('SELECT id, name, description, date, time FROM work_log')
            rows = c.fetchall()
        elif query_type == self.query_type_const["today"]:
            c.execute('SELECT id, name, description, date, time FROM work_log WHERE date = ?', (self.today,))
            rows = c.fetchall()
        elif query_type == self.query_type_const["sp_date"] and date is not None:
            c.execute('SELECT id, name, description, date, time FROM work_log WHERE date = ?', (date,))
            rows = c.fetchall()
        else:
            raise AttributeError
        
        conn.close()
        
        return rows
    
    def insert_log(self, name, scope, context, description, tags):
        """inserts a log into the database
        """
        # TODO: make variables for insert elements
        conn = sqlite3.connect(DB_FILE)
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
            (name, scope, context, desc, tags, date, time))
        conn.commit()
        conn.close()
        
        return 1
    
    def get_log_count(self, query_type="all", date=None):
        """gets count of logs based on `query_type` param
        """

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        if query_type == self.query_type_const["all"]:
            c.execute('SELECT COUNT(id) FROM work_log')
            count = c.fetchone()[0]
        elif query_type == self.query_type_const["today"]:
            c.execute('SELECT COUNT(id) FROM work_log WHERE date = ?',(self.today,))
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

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        if query_type == self.query_type_const["all"]:
            result = self.get_records()            
        elif query_type == self.query_type_const["today"]:
            result = self.get_records(query_type=self.query_type_const["today"])            
        elif query_type == self.query_type_const["sp_date"]:
            # TODO: fill in date
            result = self.get_records(query_type=self.query_type_const["sp_date"], date=False)            
        else:  
            raise AttributeError
        
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        with open(os.path.join(export_dir, self.all_records_file_name), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['ID', 'Name', 'Scope', 'Context', 'Description', 'Tags', 'Date', 'Time'])
            for row in result:
                writer.writerow(row)
        
    # ===============================================================
    # =========================== Layouts ===========================
    # ===============================================================
    
    def main_layout(self) -> list:
        """config for displaying tabs

        Returns:
            tab_group (list): pysimplegui layout lists
        """
        tab_group = [[
            sg.TabGroup([
                [sg.Tab('Log', self.entry_layout())],
                [sg.Tab('View', self.view_layout())],
                [sg.Tab("Edit", self.edit_layout())],
                [sg.Tab('About', self.about_layout())]
            ])
        ]]
        return tab_group

    def entry_layout(self) -> list:
        return [
            [sg.Text("Name:", text_color="red"), sg.Input(key="-NAME-", pad=(10, 10))],
            [sg.Text("Scope:", text_color="blue"), sg.Input(key="-SCOPE-", pad=(10, 10))],
            [sg.Text("Description:", text_color="green"), sg.Multiline(size=(40, 10), key="-DESCRIPTION-", pad=(10, 10))],
            [sg.Text("Tags:", text_color="purple"), sg.Input(key="-TAGS-", pad=(10, 10))],
            [sg.Button("Submit", key="-SUBMIT-", button_color=("white", "green"), pad=((300, 0), 10))]
        ]
    
    def view_layout(self) -> list:
        data = self.get_records()
        return [
           [sg.Table(values=data, headings=["ID", "Name", "Scope", "Context", "Description", "Tags", "Date", "Time"],
              background_color='blue', text_color='white', auto_size_columns=True,
              justification='center', alternating_row_color='lightgray',
              key="-TABLE-", num_rows=20, enable_events=True)],
            [sg.Text("Selected Row Data:", size=(None, 1)), sg.Text("", size=(None, 1), key="-SELECTED_ROW_DATA-")]
        ]
    
    def edit_layout(self) -> list:
        return [
            sg.Text("Edit Layout", font=self.section_normal_font)
        ]
    
    def about_layout(self) -> list:
        """about section layout

        Returns:
            (list): pysimplegui layout list
        """
        return [
            [
                sg.Text("📜 About Shortcut Keeper", font=self.section_title_font),
                sg.Text("(v0.1)", font=self.section_normal_font)
            ],
            [sg.HorizontalSeparator()],
            [sg.Text("This app was created by M.Hammad Hassan",
                     font=self.section_normal_font)],
            [sg.Text("using PySimpleGUI.",
                     font=self.section_normal_font)],
            [sg.Text("This is a simple Work Logger which is designed to",
                     font=self.section_normal_font)],
            [sg.Text("keep track of all your daily office tasks, with",
                     font=self.section_normal_font)],
            [sg.Text("which you can use to keep track of each individual",
                     font=self.section_normal_font)],
            [sg.Text("tasks you perform on a daily basis.",
                     font=self.section_normal_font)],
            [sg.Text("For more information, please visit:",
                     font=self.section_normal_font)],
            [sg.Text("🔗 https://github.com/Blankscreen-exe", enable_events=True, font=("Consolas", 12),
                     text_color='#0F3FD8', background_color='#B2C00D', key="-ABOUT-LINK-")]
        ]
    
    # ===============================================================
    # ======================== Main Method ==========================
    # ===============================================================
    
    def main(self) -> None:
        """Main window loop to start this app
        """
        window = self.window

        while True:

            # set theme
            sg.theme(self.app_theme)
            # read events and their values
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "WIN_CLOSED", "Exit"):
                break

            # shortcut events
            if event == "submit_button":
                path = values["path_input"]
                self.add_registered_item(path)
                window.close()
                window = sg.Window(self.get_app_title(),
                                   self.tab_group(), icon=self.app_icon)

            elif event.endswith("_delete_button"):
                index = int(event.split("_")[0])
                self.delete_registered_item(index)
                window.close()
                window = sg.Window(self.get_app_title(),
                                   self.tab_group(), icon=self.app_icon)

            elif event.endswith("_open_button"):
                index = int(event.split("_")[0])
                os.startfile(self.get_registered_item()[index])

            # hyperlink events
            elif event == "-ABOUT-LINK-":
                os.startfile("https://github.com/Blankscreen-exe/shortcut_keeper")

            # settings events
            elif event == "set_theme":
                theme = values["theme_dropdown"]
                self.reset_app_theme(theme)
                window.close()
                window = sg.Window(self.get_app_title(),
                                   self.tab_group(), icon=self.app_icon)

            elif event == "set_app_title":
                title = values["new_window_title"]
                self.reset_app_title(title)
                window.close()
                window = sg.Window(self.get_app_title(),
                                   self.tab_group(), icon=self.app_icon)

        window.close()


if __name__ == '__main__':
    App = work_diary()
    App.main()