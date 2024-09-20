# playground-snowpark-container-services

Connectivity to snowpark container services

This builds off information in [Tutorial 1][1]

## Setup

### Build and push the docker app

Build the docker app and push it up to the repository (note `/app` is the folder name):

```
cd docker-python-app
IMAGE_NAME=EXAMPLE.registry.snowflakecomputing.com/tutorial_db/alex_test_data_schema/tutorial_repository/my_echo_service:latest
docker build ./app --rm --platform linux/amd64 -t $IMAGE_NAME
docker push $IMAGE_NAME
```

### Create the Snowpark Container Services Service and expose an endpoint

Create an application (there is an assumption that you created a schema, warehouse and role with enough permissions):

```sql
DESCRIBE COMPUTE POOL tutorial_compute_pool;

DROP SERVICE IF EXISTS echo_service;

CREATE SERVICE echo_service
  IN COMPUTE POOL tutorial_compute_pool
  FROM SPECIFICATION $$
    spec:
      containers:
      - name: echo
        image: /tutorial_db/alex_test_data_schema/tutorial_repository/my_echo_service
        env:
          SERVER_PORT: 8000
          CHARACTER_NAME: Bob
        readinessProbe:
          port: 8000
          path: /healthcheck
      endpoints:
      - name: echoendpoint
        port: 8000
        public: true
      $$
   MIN_INSTANCES=1
   MAX_INSTANCES=1;
```

Ensure it's deployed

```sql
SHOW SERVICES;

SELECT SYSTEM$GET_SERVICE_STATUS('echo_service');

DESCRIBE SERVICE echo_service;
```

### 🚨 Get the latest endpoint URL 🚨

A very important step - if you haven't redeployed and you're using your old version you might get 405 Method Not Allowed because you're not using the latest version:

```sql
SHOW ENDPOINTS IN SERVICE echo_service;
```

### Redeploying the app

I'm not sure if this is the right way but I couldn't find another way to take the latest container instance so just dropped it and recreated it. In the future we could probably use blue/green with a dns to route traffic so zero downtime.

```sql
DROP SERVICE IF EXISTS echo_service;

# CREATE ... (see above)
```

### Pause and resume

Should you want to for some reason pause and resume it:

```sql
ALTER SERVICE echo_service SUSPEND;

ALTER SERVICE echo_service RESUME;

SHOW ENDPOINTS IN SERVICE echo_service;
```

## Testing the app

Open [python-client-demo/main.py](python-client-demo/main.py) and update the params at the top.

```
SNOWFLAKE_USERNAME = "todo@example.com"
SNOWFLAKE_PASSWORD = 'TODO'
SNOWFLAKE_ACCOUNT = "TODO.eu-west-1"

# Note: this changes after each deployment
# Use the following SQL to get the endpoint:
# > SHOW ENDPOINTS IN SERVICE echo_service;
SNOWFLAKE_SPCS_INGRESS_URL = "TODO"
```

Execute the script. You should not be asked to login because `token` contains the credentials.

```
cd python-client-demo
python3 ./main.py
```

## Taking it further

Should you wish to get way more advanced and make this callable in Snowflake SQL itself:

```sql
DROP FUNCTION IF EXISTS my_echo_udf(VARCHAR);

CREATE FUNCTION my_echo_udf (InputText varchar)
  RETURNS varchar
  SERVICE=echo_service
  ENDPOINT=echoendpoint
  AS '/echo';
SELECT my_echo_udf('hello world!');
```

## 404 Not Found

This can be caused by `server_session_keep_alive` not being set to `true` in the connector initialisation parameters.
Many thanks to Thanos Bantis for this suggestion.

## Links

- [Tutorial 1 - Create a Snowpark Container Services Service][1]
- [Connect to API service endpoint, hosted in Snowpark Containers using Snowpark][2]

[1]: https://docs.snowflake.com/en/developer-guide/snowpark-container-services/tutorials/tutorial-1
[2]: https://gist.github.com/sfc-gh-vsekar/4d61024cbd9ad8c7d746bc46d55a6090
