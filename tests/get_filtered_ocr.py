import requests

url = "http://localhost:8000/ocr/?date_of_issue=2022-01-01&status=active"

response = requests.get(url)
response_data = response.json()

# Assert the response status code
assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

# Assert the structure of the response data
assert "data" in response_data, "Expected 'data' key in response but not found"
assert isinstance(response_data["data"], list), "Expected 'data' to be a list"

# Print the response data
print(response_data)
