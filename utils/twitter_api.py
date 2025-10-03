import requests
import time

'''
https://data.gopher-ai.com/dashboard
https://developers.gopher-ai.com/docs/index-API/live-search#example-of-searchbyquery-or-searchbyfullarchive-response%3A

gives 403 status code: forbidden, API key might be out of date?
'''
url = "https://data.gopher-ai.com/api/v1/search/live"
headers = {
    "Authorization": "Bearer cRhwzuoFPgW3j0cBQRhPDxE1FOWIJ23SBvKWLyF5huYHraYI",
    "Content-Type": "application/json"
}
data = {
    "type": "twitter",
    "arguments": {
        "type": "searchbyquery",
        "query": "AI",
        "max_results": 10
    }
}

response = requests.post(url, headers=headers, json=data)
uuid = response.json()['uuid']

url = f"https://data.gopher-ai.com/api/v1/search/live/twitter/result/{uuid}" 
headers = {"Authorization": "Bearer cRhwzuoFPgW3j0cBQRhPDxE1FOWIJ23SBvKWLyF5huYHraYI"}
for i in range(5): 
    response = requests.get(url, headers={"Authorization": headers["Authorization"]})
    if response.status_code == 200:
        print(response.json())
        break
    else:
        print(f"Attempt {i+1}: status {response.status_code}, waiting 5s...")
        time.sleep(5)
    