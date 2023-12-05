import requests

ocr_id = "1234567890"  # Replace with the actual ID
url = f"http://localhost:8000/ocr/{ocr_id}"

response = requests.get(url)
response_data = response.json()

# Assert the response status code
assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

# Assert the structure of the response data
assert "data" in response_data, "Expected 'data' key in response but not found"
assert isinstance(response_data["data"], dict), "Expected 'data' to be a dictionary"

# Print the response data
print(response_data)
