from work_diary_api import work_diary
import unittest
import os
import sqlite3
from pprint import pprint as pp

api = work_diary()

class work_diary_tests(unittest.TestCase):
    
    def setUp(self):
        for i in range(30):
            api.insert_record(
                name=f"task {i}",
                scope=f"scope {i}",
                context=f"ctxt {i}",
                description=f"desc {i}",
                tags=f"{i*1}, {i*2}, {i*3}"
                )
    
    def tearDown(self):
        # Connect to the database
        conn = sqlite3.connect('.\\log_test.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM work_log")
        conn.commit()

        # Reset the auto-increment to 0
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='work_log'")
        conn.commit()
        cursor.execute("VACUUM")
        conn.commit()

        # Close the database connection
        conn.close()
    
    def test_insert_record(self):
        api.insert_record(
                name=f"banana muffin",
                scope=f"baking",
                context=f"kitchen",
                description=f"baking a muffin, only single one",
                tags=f"baking, cooking, kitchen"
                )
    
    def test_read_records(self):
        data = api.get_records()
        self.assertEqual(len(data), 30)
    
    def test_get_log_count(self):
        count = api.get_log_count(query_type="all")
        self.assertEqual(count, 30)
        
        count = api.get_log_count(query_type="today")
        self.assertEqual(count, 30)
        
        count = api.get_log_count(query_type="sp_date", date="22-06-2023")
        print(count)
        self.assertEqual(count, 30)
        
    def test_update_record(self):
        api.update_record(2, data={
            "name":"super"
            })
        result = api.get_records(query_type="all")
        self.assertEqual(result[1][1], "super")
        
        api.update_record(3, data={
            "description":"crap",
            "name": "magicrap"
            })
        result = api.get_records(query_type="all")
        self.assertEqual(result[2][1], "magicrap")
        self.assertEqual(result[2][4], "crap")
        
        api.update_record(5, data={
            "tags":"4,4,4,4",
            "date": "7-3-2021"
            })
        result = api.get_records(query_type="all")
        self.assertEqual(result[4][5], "4,4,4,4")
        self.assertEqual(result[4][6], "7-3-2021")
        
    def test_delete_record(self):
        for i in range(10):
            api.delete_record(5+i)
        
        self.assertLess(api.get_log_count(), 30)
        self.assertEqual(api.get_log_count(), 20)
        
    def test_get_records_by_range(self):
        for i in range(5):
            api.update_record(1+i, data={
                "date": "20-06-2023"
                })
        for i in range(5):
            api.update_record(6+i, data={
                "date": "21-06-2023"
                })
        count = api.get_records(query_type="sp_date", date=("22-06-2023", "22-06-2023"))        
        
        self.assertEqual(len(count), 20)
        count = api.get_records(query_type="sp_date", date=("21-06-2023", "22-06-2023"))
        self.assertEqual(len(count), 25)
        
    def test_get_record_by_id(self):
        result = api.get_records(query_type="id", id=3)
        self.assertEqual(result[0][0], 3)
        self.assertEqual(result[0][1], "task 2")
        self.assertEqual(result[0][5], "2, 4, 6")
        

if __name__ == '__main__':
    unittest.main()