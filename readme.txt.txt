Flask-migrate:
	$ flask db init
	$ flask db migrate -m "Initial migration."
	$ flask db upgrade

Adding macros to excel file:
	extract vbaProject.bin:
		$ C:\Users\LogisticsUser02\Documents\VIN_import\venv\Scripts\vba_extract.py "C:\Users\LogisticsUser02\Documents\VIN_import\backend\ok_units_macro.xlsm
		$ workbook.add_vba_project(r'C:\Users\LogisticsUser02\Documents\VIN_import\backend\vbaProject.bin')
