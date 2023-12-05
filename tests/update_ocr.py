import requests

url = "http://localhost:8000/ocr/update/"

data = {
    "identification_number": "1234567890",
    "first_name": "Jane",
    "last_name": "Doe",
    "date_of_birth": "1990-02-02",
    "date_of_issue": "2022-02-02",
    "date_of_expiry": "2025-02-02"
}

response = requests.put(url, json=data)
response_data = response.json()

# Assert the response status code
assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

# Assert the message from the response
assert response_data.get("message") == "Record updated successfully", "Record update failed"

# Print the response data
print(response_data)
