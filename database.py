# database.py

import sqlite3
from fastapi import HTTPException
from models import OCRResult

conn = sqlite3.connect("./test.db")
cursor = conn.cursor()

def create_ocr_record(ocr_data: OCRResult):
    query = """
    INSERT INTO id_card_database 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        # Check for unreadable or unclear ID card data
        if not ocr_data.identification_number or not ocr_data.name:
            raise HTTPException(status_code=422, detail="Unreadable or unclear ID card data")
        
        status = "active"
        timestamp = str(datetime.now().timestamp())

        cursor.execute(query, (
            ocr_data.identification_number,
            ocr_data.name,
            ocr_data.last_name,
            ocr_data.date_of_birth,
            ocr_data.date_of_issue,
            ocr_data.date_of_expiry,
            ocr_data.status,
            ocr_data.timestamp
            #add staus
            #add timestamp
        ))
        conn.commit()
        return ocr_data
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Record already exists")

def get_ocr_record(identification_number: str):
    query = """
    SELECT * FROM id_card_database WHERE identification_number = ?
    """
    cursor.execute(query, (identification_number,))
    result = cursor.fetchone()
    if result:
        return {
            "identification_number": result[0],
            "name": result[1],
            "last_name": result[2],
            "date_of_birth": result[3],
            "date_of_issue": result[4],
            "date_of_expiry": result[5],
            "status": result[6],
            "timestamp":result[7]
        }
    raise HTTPException(status_code=404, detail="Record not found")

def get_filtered_ocr_records(date_of_issue: str = None, status: str = None):
    query = "SELECT * FROM id_card_database WHERE 1"
    params = []

    if date_of_issue:
        query += " AND date_of_issue = ?"
        params.append(date_of_issue)
    
    if status:
        query += " AND status = ?"
        params.append(status)

    cursor.execute(query, params)
    results = cursor.fetchall()
    ocr_records = []
    for result in results:
        ocr_records.append({
            "identification_number": result[0],
            "name": result[1],
            "last_name": result[2],
            "date_of_birth": result[3],
            "date_of_issue": result[4],
            "date_of_expiry": result[5],
            "status": result[6],
            "timestamp":result[7]
        })
    return ocr_records

def delete_ocr_record(identification_number: str):
    query = """
    DELETE FROM id_card_database WHERE identification_number = ?
    """
    cursor.execute(query, (identification_number,))
    conn.commit()
    return {"message": "Record deleted successfully"}

def update_ocr_record(ocr_data: OCRResult):
    query = """
    UPDATE id_card_database
    SET filename = ?, name = ?, last_name = ?, date_of_birth = ?, date_of_issue = ?, date_of_expiry = ?
    WHERE identification_number = ?
    """
    try:
        cursor.execute(query, (
            ocr_data.filename,
            ocr_data.name,
            ocr_data.last_name,
            ocr_data.date_of_birth,
            ocr_data.date_of_issue,
            ocr_data.date_of_expiry,
            ocr_data.identification_number,
            ocr_data.status,
            ocr_data.timestamp
        ))
        conn.commit()
        return {"message": "Record updated successfully"}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Invalid data provided")