from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.templating import Jinja2Templates
import shutil
import os
from pydantic import BaseModel
from databases import Database
import sqlite3
import base64
import requests
import json
import datetime
from datetime import datetime
import re
from starlette.requests import Request
from databases import Database
# main.py
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from database import (
    create_ocr_record,
    get_ocr_record,
    get_filtered_ocr_records,
    delete_ocr_record
)
from models import OCRResult

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
database = Database(DATABASE_URL)

# Connect to SQLite database
conn = sqlite3.connect("./test.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS id_card_database (
        identification_number TEXT PRIMARY KEY,
        name TEXT,
        last_name TEXT,
        date_of_birth TEXT,
        date_of_issue TEXT,
        date_of_expiry TEXT,
        status TEXT,
        timestamp TEXT
    )
""")
conn.commit()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# Google Cloud Vision API endpoint and API key
ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
api_key = "AIzaSyCOxNkK0N3jTNRXSN0ThHGf2R4frIIQr14"

# Function to create image data for OCR
def makeImageData(imgpath):
    img_req = None
    with open(imgpath, 'rb') as f:
        ctxt = base64.b64encode(f.read()).decode()
        img_req = {
            'image': {
                'content': ctxt
            },
            'features': [{
                'type': 'DOCUMENT_TEXT_DETECTION',
                'maxResults': 1
            }]
        }
    return json.dumps({"requests": img_req}).encode()

# Function to perform OCR using Google Cloud Vision API
def requestOCR(url, api_key, imgpath):
    imgdata = makeImageData(imgpath)
    response = requests.post(url,
                             data=imgdata,
                             params={'key': api_key},
                             headers={'Content-Type': 'application/json'})
    return response

def get_db():
    db_connection = sqlite3.connect("test.db")
    try:
        yield db_connection
    finally:
        db_connection.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_and_process(request: Request, file: UploadFile = File(...)):
    if not file.content_type.startswith("image"):
        raise HTTPException(status_code=400, detail="File must be an image")

    if file.file.tell() > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size too large. Max file size is 2MB")

    file_extension = file.filename.split(".")[-1]
    if file_extension.lower() not in ["png", "jpeg", "jpg"]:
        raise HTTPException(status_code=400, detail="File must be in PNG, JPEG, or JPG format")

    with open(f"uploaded_files/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Perform OCR using Google Cloud Vision API
    result = requestOCR(ENDPOINT_URL, api_key, f"uploaded_files/{file.filename}")

    if result.status_code != 200 or result.json().get('error'):
        return {"error": "OCR processing failed"}
    else:
        # Extracted OCR information
        result = result.json()['responses'][0]['textAnnotations']
        original_text = result[0]['description']
        lines = original_text.split('\n')
        filtered_lines = [line for line in lines if re.search(r'[^\x00-\x7F]', line) is None]
        date_pattern = re.compile(r'\b(\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s\d{4}|\d{1,2}\s\d{1,2}\.?\s\d{4}|\d{4}-\d{2}-\d{2})\b')

# Extract and print lines that contain dates
        date_lines = [line for line in filtered_lines if date_pattern.search(line)]

# Print the lines with dates
        Date_of_birth=0
        Date_of_issue=0
        Date_of_expiry=0
        k=0
        for line in date_lines:
            if(k==0):
                Date_of_birth=line
                k=1
            elif(k==1):
                Date_of_issue=line
                k=2
            else:
                Date_of_expiry=line
                k=3

        if '.' in Date_of_birth:
    # Remove the dot if present
            Date_of_birth = Date_of_birth.replace('.', '')

        if '.' in Date_of_issue:
    # Remove the dot if present
            Date_of_issue = Date_of_issue.replace('.', '')
        if '.' in Date_of_expiry:
    # Remove the dot if present
            Date_of_expiry = Date_of_expiry.replace('.', '')
        Date_of_birth = Date_of_birth.replace('Date of Birth ', '')

#first name and last name
        name_pattern = re.compile(r'Name (.+)')
        last_name_pattern = re.compile(r'Last name (.+)')

        first_name = None
        last_name = None

        for line in filtered_lines:
            name_match = name_pattern.match(line)
            last_name_match = last_name_pattern.match(line)

            if name_match:
                first_name = name_match.group(1)
            elif last_name_match:
                last_name = last_name_match.group(1)


# Regular expression to match all digits
        all_digits_pattern = re.compile(r'\d+')

# Concatenate all digits from each line
        concatenated_digits = ""
        for line in filtered_lines:
            digits = all_digits_pattern.findall(line)
            concatenated_digits += ''.join(digits)

# Extract and convert the first 13 digits to a string
        first_13_digits = str(concatenated_digits[:13])
        identification_number = first_13_digits
        
        current_status = "active"
        current_time = str(datetime.now().timestamp())

# Convert timestamp to string format
        output_json = {
            "identification_number": identification_number,
            "first_name": first_name,
            "last_name": last_name,
            "Date_of_birth": Date_of_birth,
            "Date_of_issue": Date_of_issue,
            "Date_of_expiry": Date_of_expiry,
            "status":current_status,
            "timestamp":current_time
        }

        
        # Convert to JSON format
        

        
        try:
            # Attempt to insert data into the SQLite database
            cursor.execute("""
                INSERT INTO id_card_database
                (identification_number, name, last_name, date_of_birth, date_of_issue, date_of_expiry,status,timestamp) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (identification_number, first_name, last_name, Date_of_birth, Date_of_issue, Date_of_expiry,current_status,current_time))
            conn.commit()

        except sqlite3.IntegrityError:
            return JSONResponse(output_json)

        # Return the result
        return JSONResponse(output_json)

# Endpoint to create OCR record
@app.post("/ocr/create/")
async def handle_create_ocr_record(ocr_data: OCRResult):
    try:
        created_record = create_ocr_record(ocr_data)
        return {"message": "Record created successfully", "data": created_record}
    except HTTPException as e:
        return {"error": str(e)}

# Endpoint to get OCR record
@app.get("/ocr/{identification_number}")
async def handle_get_ocr_record(identification_number: str):
    try:
        record = get_ocr_record(identification_number)
        return {"data": record}
    except HTTPException as e:
        return {"error": str(e)}

# Endpoint to get filtered OCR records
@app.get("/ocr/")
async def handle_get_filtered_ocr_records(date_of_issue: str = None, status: str = None):
    try:
        filtered_records = get_filtered_ocr_records(date_of_issue, status)
        return {"data": filtered_records}
    except HTTPException as e:
        return {"error": str(e)}

# Endpoint to delete OCR record
@app.delete("/ocr/{identification_number}")
async def handle_delete_ocr_record(identification_number: str):
    try:
        delete_ocr_record(identification_number)
        return {"message": "Record deleted successfully"}
    except HTTPException as e:
        return {"error": str(e)}
    
@app.get("/create_response", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("create_response.html", {"request": request})

@app.get("/read_response", response_class=HTMLResponse)
def read_data():
    # Connect to the SQLite database
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()

    try:
        # Execute a query to retrieve data
        cursor.execute("SELECT * FROM id_card_database")
        data = cursor.fetchall()
    except Exception as e:
        # Handle exceptions, such as table not found or other errors
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Close the database connection
        conn.close()

    # Format the data for display in HTML
    entries_html = "<table border='1'><tr><th>ID</th><th>Name</th><th>Last Name</th><th>Date of Birth</th><th>Date of Issue</th><th>Date of Expiry</th><th>Status</th><th>Timestamp</th></tr>"
    for entry in data:
        entries_html += "<tr>"
        for value in entry:
            entries_html += f"<td>{value}</td>"
        entries_html += "</tr>"
    entries_html += "</table>"

    # HTML response to be displayed
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Read Data Response</title>
    </head>
    <body>
        <h1>Read Data Response</h1>
        {entries_html}
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)

class UserData(BaseModel):
    identification_number: str
    first_name: str
    last_name: str
    date_of_birth: str
    date_of_issue: str
    date_of_expiry: str

@app.get("/create_response", response_class=HTMLResponse)
async def create_page(request: Request):
    return templates.TemplateResponse("create_response.html", {"request": request})

@app.post("/submit_data")
async def submit_data(user_data: UserData):
    # Convert current timestamp to string
    current_timeofentry = str(datetime.now().isoformat())

    # Add the timestamp to the user data
    current_status = "active"
    # Insert data into the SQLite database
    # conn = sqlite3.connect("test.db")
    # cursor = conn.cursor()
    output_json = {
            "identification_number": user_data.identification_number,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "Date_of_birth": user_data.date_of_birth,
            "Date_of_issue": user_data.date_of_issue,
            "Date_of_expiry": user_data.date_of_expiry,
            "status":current_status,
            "timestamp":current_timeofentry
        }

    try:
        cursor.execute('''
            INSERT INTO id_card_database (
                identification_number, name, last_name,
                date_of_birth, date_of_issue, date_of_expiry, status, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data.identification_number, user_data.first_name,
            user_data.last_name, user_data.date_of_birth, user_data.date_of_issue,
            user_data.date_of_expiry, current_status, current_timeofentry
        ))

        conn.commit()
    except sqlite3.IntegrityError:
        return {"message": "Error: Identification Number already exists."}
    finally:
        conn.close()

    return {"message": "Data submitted successfully!"}

@app.get("/update_response", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("update_response.html", {"request": request})

@app.get("/delete_response", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("delete_response.html", {"request": request})

