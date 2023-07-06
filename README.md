# Hono Migration Tool

Application migrates registries, devices, credentials and configs from Google's iot core to Hono.


<br>

## Authentication

There are 2 methods to authenticate with the application:

1.   <b>Running application on Google Cloud<b>. 

     If you’re running in a Google Virtual Machine Environment (Compute Engine, App Engine, Cloud Run, Cloud Functions), authentication should “just work”.


2.   <b>Using Service Account json key<b>.

     If you’re running your application elsewhere, you should download a service account JSON keyfile and point to it using an environment variable:

     ``
     $ export GOOGLE_APPLICATION_CREDENTIALS="/path/to/keyfile.json"
     ``
     
     or use the --key argument to pass the key path to the service account.

     Account should have the roles:
     
     1. Cloud IoT Core Service Agent
     2. Cloud IoT Viewer
     3. Cloud Trace Agent
     4. IAP-secured Web App User (for the project to which the devices should be migrated to)
     5. Pub/Sub Editor
     6. Service Controller
     
     

<br>

## Running the application

<br>

To run the application, use the <b> output/hono_migration_tool.exe file<b>.

EXE file was created with <a href="https://towardsdatascience.com/how-to-easily-convert-a-python-script-to-an-executable-file-exe-4966e253c7e9#c689">Pylancher</a>.


<br>

## Line Args

| Line Args          | Mandatory | Description                                                                                                                            |
|--------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------|
| -p,  <br>--project | Yes       | Google Cloud Project ID (migration source)                                                                                             |
| -k,  <br>--key     | Yes       | Service Account Json Key path                                                                                                          |
| -u, <br>--api      | Yes       | Hono device registry api url (migration target), <br>  example  https://my_hono_api/v1                                                 |
| -a,<br>--audience  | Yes       | Target audience (OAuth 2.0 Client), <br>example 837927849228-js9djh3li9shfut7hfbcjjapsjf8d86s.apps.googleusercontent.com               |
| -t,  --tenant      | Yes        | The Hono tenant ID                           |
| -reg,  --registry      | Yes        | The Google IoT Core registry to migrate                           |
| -r, <br>--region   | No        | Google Cloud Region (migration source). <br>Valid regions are: {asia-east1,europe-west1,us-central1} <br>Default is <b>europe-west1<b> |
| --migrate_gateways | No | Boolean flag indicating whether to migrate gateways or not |

<br>


## Running the application examples

<br>

EXE file:

````
hono_migration_tool.exe
--project my-project  
--api https://my_hono_api/v1 
--region europe-west1 
--tenant test-1
--registry hono-registry-1
--audience 837927849228-js9djh3li9shfut7hfbcjjapsjf8d86s.apps.googleusercontent.com  --key .\hono-cloud-endpoint-manager.json

````

<br>


Python file:

````
python.exe app.py 
--project my-project
--api https://my_hono_api/v1 
--region europe-west1 
--tenant test-1
--registry hono-registry-1
--audience 837927849228-js9djh3li9shfut7hfbcjjapsjf8d86s.apps.googleusercontent.com  --key .\hono-cloud-endpoint-manager.json

````
<br>

## Gateways migration

<br>

Gateways from IoT Core will be migrated as devices to Hono.
To migrate gateways args flag **--migrate_gateways** should be set.

example:

````
python.exe app.py 
--project my-project 
--api https://my_hono_api/v1
--region europe-west1 
--audience 837927849228-js9djh3li9shfut7hfbcjjapsjf8d86s.apps.googleusercontent.com  --key .\hono-cloud-endpoint-manager.json
--migrate_gateways
````