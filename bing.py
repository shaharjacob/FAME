import json
import os
import requests
from pprint import pprint


# Add your Bing Autosuggest subscription key and endpoint to your environment variables.
os.environ['BING_AUTOSUGGEST_SUBSCRIPTION_KEY'] = '1dfd0b4c80104d4d8dd0e0a9e6080187'
os.environ['BING_AUTOSUGGEST_ENDPOINT'] = 'https://api.bing.microsoft.com/'

subscription_key = os.environ['BING_AUTOSUGGEST_SUBSCRIPTION_KEY']
endpoint = os.environ['BING_AUTOSUGGEST_ENDPOINT'] + 'v7.0/Suggestions/'

# Construct the request
mkt = 'en-US'
query = 'why does earth .* sun'
params = { 'q': query, 'mkt': mkt }
headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

# Call the API
try:
    response = requests.get(endpoint, headers=headers, params=params)
    res = response.json()
    print(res)
except:
    print("")