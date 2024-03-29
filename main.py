import PySimpleGUI as sg
import os
import json
import csv
import sqlite3
from datetime import datetime

from pprint import pprint as pp

from work_diary_api import work_diary

class App():
    """
    This class represents an app that allows users to register and view quick launch shortcuts.
    """
    
    # initialize diary
    diary = work_diary()
    
    def __init__(self):
        # app settings
        self.app_theme = "Reddit"
        sg.theme(self.app_theme)
        self.app_icon = "./book.ico"
        self.window_size = (300, 220)
        self.section_title_font = ("MS Sans Serif", 14)
        self.section_normal_font = ("MS Sans Serif", 10)
        self.section_normal_bold_font = ("MS Sans Serif", 10, 'bold')
        self.section_link_font = ("MS Sans Serif", 10)
        self.window = sg.Window(
                                "Work Diary",
                                self.main_layout(), 
                                icon=self.app_icon
                                )
        
        # database config
        self.today = datetime.today().strftime('%d-%m-%Y')
        self.query_type_const = {
            "all": "all",
            "today": "today",
            "sp_date": "sp_date",
        }
        
        # export/import config
        self.export_dir = "logs"
        self.all_records_file_name = 'all_export'
        self.export_file_prefix = 'work_diary_'
        self.export_file_suffix = '_report'
    
    # ===============================================================
    # ========================= App Actions =========================
    # ===============================================================
    ACTIONS = {
        0: "insert_record",
        1: "delete_record",
        2: "update_record",
        3: "read_records",
        4: "read_one_record",
        5: "export",
        6: "import",
        7: "goto_link_about",
    }
    
    # ===============================================================
    # ====================== Action Functions =======================
    # ===============================================================
    
    def insert_record(self, data) -> None:
        self.diary.insert_record(
            name=data['name'],
            scope=data['scope'],
            context=data['context'],
            description=data['description'],
            tags=data['tags']
        )
        
    def read_record(self, query_type, id, start_date, end_date):
        # TODO:check if date is a tuple or a string, then pass the date accordingly
        date = self.date_param_manipulator(start_date, end_date)
        
        self.diary.get_records(
            query_type=query_type,
            id=id,
            date=date
        )
        
    def update_record(self, id, data):
        # TODO: prepare a data packet to pass in the function
        self.diary.update_record(
            id=id,
            data=data
        )
    
    def delete_record(self, id):
        self.diary.delete_record(
            id=id
        )
    
    # ===============================================================
    # ====================== Action Utilities =======================
    # ===============================================================
    
    def date_param_manipulator(self, date_start, date_end):
        return date_start if date_end == None else (date_start, date_end,)
    
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
        """log entry section layout

        Returns:
            (list): pysimplegui layout list
        """
        return [
            [sg.Text("📜 Log Entry", font=self.section_title_font)],
            [sg.Text("Make an entry of your record to the database.", font=self.section_normal_font)],
            [sg.Text("Name:      "), sg.Input(key="-NAME-", pad=(10, 9))],
            [sg.Text("Scope:     "), sg.Input(key="-SCOPE-", pad=(10, 9))],
            [sg.Text("Context:   "), sg.Input(key="-CTXT-", pad=(10, 9))],
            [sg.Text("Description:"), sg.Multiline(size=(40, 10), key="-DESC-", pad=(10, 9))],
            [sg.Text("Tags:        "), sg.Input(key="-TAGS-", pad=(10, 10))],
            [sg.Button("Submit", key="-SUBMIT-", pad=((300, 0), 9))]
        ]
    
    def view_layout(self, query_type="all", date=None, id=None) -> list:
        """view section layout

        Returns:
            (list): pysimplegui layout list
        """
        data = self.diary.get_records(query_type=query_type, id=id, date=date)
        return [
            [sg.Text("📜 View Logs", font=self.section_title_font)],
            [sg.Text("View existing records. Select any record from the table to view its details.", font=self.section_normal_font)],
            [
               sg.Table(
                   values=data, 
                   headings=["ID", "Name", "Scope", "Context", "Description", "Tags", "Date", "Time"],
                # table colors
                   background_color='#ECECEC', 
                   text_color='black', 
                   alternating_row_color='#FAFAFA',
                # sizing config
                    #auto_size_columns=True,
                   justification='center', 
                   num_rows=20, 
                   max_col_width=5,
                   def_col_width=5,
                   vertical_scroll_only=False,
                   expand_x=True,
                # font
                   font=self.section_normal_font,
                # event management
                   key=self.ACTIONS[3], 
                   enable_events=True)
            ],
            [
                sg.Text("ID: ", size=(None, 1), font=self.section_normal_bold_font, text_color="#1399D4"), 
                sg.Text("", size=(None, 1), font=self.section_normal_font, auto_size_text=True, key="-DATA_VIEW-ID-"),
                sg.Text("DATE: ", size=(None, 1), font=self.section_normal_bold_font, text_color="#1399D4"), 
                sg.Text("", size=(None, 1), font=self.section_normal_font, auto_size_text=True, key="-DATA_VIEW-DATE-"),
                sg.Text("TIME: ", size=(None, 1), font=self.section_normal_bold_font, text_color="#1399D4"), 
                sg.Text("", size=(None, 1), font=self.section_normal_font, auto_size_text=True, key="-DATA_VIEW-TIME-"),
            ],
            [
                sg.Text("Name: ", size=(None, 1), font=self.section_normal_bold_font, text_color="#1399D4"), 
                sg.Text("", size=(None, 1), font=self.section_normal_font, auto_size_text=True, key="-DATA_VIEW-NAME-"),
            ],
            [
                sg.Text("Scope: ", size=(None, 1), font=self.section_normal_bold_font, text_color="#1399D4"), 
                sg.Text("", size=(None, 1), font=self.section_normal_font, auto_size_text=True, key="-DATA_VIEW-SCOPE-"),
            ],
            [
                sg.Text("Context: ", size=(None, 1), font=self.section_normal_bold_font, text_color="#1399D4"), 
                sg.Text("", size=(None, 1), font=self.section_normal_font, auto_size_text=True, key="-DATA_VIEW-CTXT-"),
            ],
            [
                sg.Text("Description: ", size=(None, 1), font=self.section_normal_bold_font, text_color="#1399D4"), 
                sg.Text("", size=(None, 1), font=self.section_normal_font, auto_size_text=True, key="-DATA_VIEW-DESC-"),
            ],
            [
                sg.Text("Tags: ", size=(None, 1), font=self.section_normal_bold_font, text_color="#1399D4"), 
                sg.Text("", size=(None, 1), font=self.section_normal_font, auto_size_text=True, key="-DATA_VIEW-TAGS-"),
            ],
            
        ]
    
    def edit_layout(self) -> list:
        """edit section layout

        Returns:
            (list): pysimplegui layout list
        """
        return [
            [sg.Text("📜 Update Logs", font=self.section_title_font)],
            [sg.Text("Update existing records. You must know the ID of the record you want to update.", font=self.section_normal_font)],
            [sg.Text("Edit Layout", font=self.section_normal_font)]
        ]
    
    def about_layout(self) -> list:
        """about section layout

        Returns:
            (list): pysimplegui layout list
        """
        return [
            [
                sg.Text("📜 About Work Diary", font=self.section_title_font),
                sg.Text("(v0.1)", font=self.section_normal_font)
            ],
            [sg.HorizontalSeparator()],
            # TODO: do a better description
            [sg.Text("This app was created by M.Hammad Hassan",
                     font=self.section_normal_font)],
            [sg.Text("This is a simple Work Logger which",
                     font=self.section_normal_font)],
            [sg.Text("is designed to keep track of all",
                     font=self.section_normal_font)],
            [sg.Text("your daily office tasks you",
                     font=self.section_normal_font)],
            [sg.Text("perform on a daily basis.",
                     font=self.section_normal_font)],
            [sg.Text("For more information, please visit:",
                     font=self.section_normal_font)],
            # TODO: add app landing page link or github readme
            [sg.Text("🔗 https://github.com/Blankscreen-exe", enable_events=True, font=self.section_link_font,
                     text_color='#0055FF', background_color='#EAEAEA', key="-ABOUT-LINK-")]
        ]
    
    # ===============================================================
    # ======================== Main Method ==========================
    # ===============================================================
    
    def main(self) -> None:
        """Main window loop to start this app
        """
        window = self.window.finalize()
        window.size(800, 600)
        # sg.show_debugger_window(location = (None, None))
        while True:

            # set theme
            sg.theme(self.app_theme)
            # read events and their values
            event, values = window.read()

            # ------------------ Close window ------------------
            if event in (sg.WIN_CLOSED, "WIN_CLOSED", "Exit"):
                break

            # ------------------ Insert Record ------------------
            if event == self.ACTIONS[0]:
                # TODO: insert record to database
                data = values["path_input"]
                print("recorded data")
                pp(data)
                
            # ------------------ Delete Record ------------------
            elif event == self.ACTIONS[1]:
                # TODO: delete record from database
                index = int(event.split("_")[0])
                print("deleted data")

            # ------------------ Update Record ------------------
            elif event == self.ACTIONS[2]:
                # TODO: update record in database
                index = int(event.split("_")[0])
                print("updated data")

            # ------------------ Read Record(s) ------------------
            elif event == self.ACTIONS[3]:
                # TODO: read records from database                
                print("read data")
                selected_row = values[self.ACTIONS[3]][0] + 1
                selected_data = self.diary.get_records(query_type="id", id=selected_row)[0]
                selected_text = f"ID: {selected_data[0]}, Name: {selected_data[1]}, Scope: {selected_data[2]}, Context: {selected_data[3]}, Description: {selected_data[4]}, Tags: {selected_data[5]}, Date: {selected_data[6]}, Time: {selected_data[7]}"
                # window["-SELECTED_ROW_DATA-"].update(selected_text)
                window["-DATA_VIEW-ID-"].update(selected_data[0])
                window["-DATA_VIEW-NAME-"].update(selected_data[1])
                window["-DATA_VIEW-SCOPE-"].update(selected_data[2])
                window["-DATA_VIEW-CTXT-"].update(selected_data[3])
                window["-DATA_VIEW-DESC-"].update(selected_data[4])
                window["-DATA_VIEW-TAGS-"].update(selected_data[5])
                window["-DATA_VIEW-DATE-"].update(selected_data[6])
                window["-DATA_VIEW-TIME-"].update(selected_data[7])
                print(selected_data)

            # ------------------ Export Records ------------------
            elif event == self.ACTIONS[5]:
                # TODO: export data to preferred format
                print("exported data")

            # ------------------ Import Record ------------------
            elif event == self.ACTIONS[6]:
                # TODO: import data from prefered format
                print("imported data")

            # ------------------ Goto Official page ------------------
            elif event == self.ACTIONS[7]:
                # TODO: add a persoinalized go to page link
                print("activated link official page")
                os.startfile("https://github.com/Blankscreen-exe/shortcut_keeper")
                
        window.close()


if __name__ == '__main__':
    app = App()
    app.main()
    print(app.diary.get_records())