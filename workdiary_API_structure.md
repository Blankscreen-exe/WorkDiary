# WORK_DIARY API

## Attributes:

🔴 **db_filename** = 'log.db'

🔴 **db_filepath** = path.join('.', 'log.db')

🔴 **export_filename_prefix** = 'work_log_('

🔴 **export_filename_suffix** = ')'

🔴 **export_filepath** = path.join('.', 'exports')

## Methods:

🔴 **log**(_self_, data={})

🔴 **get_records**(_self_, query_type="all", date=(0,0))

🔴 **edit_record**(_self_, record_id, new_data={})

🔴 **delete_record**(_self_, record_id, new_data={})

🔴 **export_data**(_self_,  type="csv", date=(0,0))

🔴 **import_data**(_self_, type="csv", path)

🔴 **store_in_cloud**(_self_)

🔴 **import_from_cloud**(_self_)

🔴 **gen_csv**(_self_, query_type="all", date=(0,0))

🔴 **gen_pdf**(_self_, query_type="all", date=(0,0))
