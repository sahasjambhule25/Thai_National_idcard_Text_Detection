import requests

ocr_id = "1234567890"  # Replace with the actual ID
url = f"http://localhost:8000/ocr/{ocr_id}"

response = requests.delete(url)
#soft delete 
#status = 
response_data = response.json()

# Assert the response status code
assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

# Assert the message from the response
assert response_data.get("message") == "Record deleted successfully", "Record deletion failed"

# Print the response data
print(response_data)
