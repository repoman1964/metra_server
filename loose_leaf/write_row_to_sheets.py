import gspread
from google.oauth2.service_account import Credentials

def write_row_to_google_sheet(sheet_id, sheet_name, row_data, creds_json_path):
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Authenticate using the service account JSON file
    creds = Credentials.from_service_account_file(creds_json_path, scopes=scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(sheet_name)

    # Append the row data
    worksheet.append_row(row_data)

# Example usage
sheet_id = 'your-google-sheet-id'  # Find this in the URL of your Google Sheet
sheet_name = 'Sheet1'
row_data = ['Data1', 'Data2', 'Data3']
creds_json_path = 'path-to-your-creds-json-file.json'

write_row_to_google_sheet(sheet_id, sheet_name, row_data, creds_json_path)
