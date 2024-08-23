import snowflake.connector
import requests

SNOWFLAKE_USERNAME = "todo@example.com"
SNOWFLAKE_PASSWORD = 'TODO'
SNOWFLAKE_ACCOUNT = "TODO.eu-west-1"

# Note: this changes after each deployment
# SHOW ENDPOINTS IN SERVICE echo_service;
SNOWFLAKE_SPCS_INGRESS_URL = "" 

def get(url):
  headers = {'Authorization': f'Snowflake Token={token}'}
  print(f'Sending get to: {url} headers: {headers}')
  response = requests.get(f'{url}', headers=headers)
  print(f'Response status: {response.status_code} body: {response.text}\n')

def post(url, body, token):
  headers = {'Authorization': f'Snowflake Token={token}', 'Content-Type': 'application/json'}
  print(f'Sending post to: {url} body: {body}: headers: {headers}')
  response = requests.post(f'{url}', json=body, headers=headers)
  print(f'Response status: {response.status_code} body: {response.text}\n')

def get_token():
  ctx = snowflake.connector.connect(
   user=SNOWFLAKE_USERNAME,# username
   password=SNOWFLAKE_PASSWORD, # insert password here
   account=SNOWFLAKE_ACCOUNT,
   session_parameters={
      'PYTHON_CONNECTOR_QUERY_RESULT_FORMAT': 'json'
   })
  # Obtain a session token.
  token_data = ctx._rest._token_request('ISSUE')
  token_extract = token_data['data']['sessionToken']
  # Create a request to the ingress endpoint with authz.
  token = f'\"{token_extract}\"'
  return token

token = get_token()

# GET endpoints
get(f'https://{SNOWFLAKE_SPCS_INGRESS_URL}/healthcheck') # Response status: 200 body: I'm ready!
get(f'https://{SNOWFLAKE_SPCS_INGRESS_URL}/healthcheck2') # Response status: 200 body: I'm ready too!

# post /sample_pos
post(f'https://{SNOWFLAKE_SPCS_INGRESS_URL}/sample_pos', None, token) # works
post(f'https://{SNOWFLAKE_SPCS_INGRESS_URL}/sample_pos', {}, token) # works

# post /echo
post(f'https://{SNOWFLAKE_SPCS_INGRESS_URL}/echo', None, token) # 400 bad request ()
post(f'https://{SNOWFLAKE_SPCS_INGRESS_URL}/echo', {}, token) # 500 error (payload is bad)
post(f'https://{SNOWFLAKE_SPCS_INGRESS_URL}/echo', { 'data': ["hello world"] }, token) # Response status: 200 body: {"data":[["h","Bob said e"]]}