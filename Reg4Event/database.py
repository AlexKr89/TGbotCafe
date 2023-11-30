import openpyxl

class Database:
    def __init__(self, filename):
        self.filename = filename

    def get_events(self):
        wb = openpyxl.load_workbook(self.filename)
        sheet = wb.active
        events = [(row[0].value, row[1].value) for row in sheet.iter_rows(min_row=2, values_only=True) if row[0].value and row[1].value]
        wb.close()
        return events