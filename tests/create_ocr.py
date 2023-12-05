import requests

url = "http://localhost:8000/ocr/create/"

data = {
    "identification_number": "1 02071 441 1",
    "filename": "example.jpg",
    "name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "date_of_issue": "2022-01-01",
    "date_of_expiry": "2025-01-01"
}

response = requests.post(url, json=data)
response_data = response.json()

# Assert the response status code
assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

# Assert the message from the response
assert response_data.get("message") == "Record created successfully", "Record creation failed"

# Print the response data
print(response_data)
