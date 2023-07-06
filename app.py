import argparse
from iot_core import IotCore
from hono_migration import HonoMigrator
from gcp_token import TokenCreator
from api import HonoDeviceApi
import os
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)
GOOGLE_CREDENTIAL_ENV_VARIABLE = "GOOGLE_APPLICATION_CREDENTIALS"

argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--project", help="Google Cloud Project ID",
                       required=True)  
argParser.add_argument("-k", "--key", help="Service Account Json Key path",
                       required=False, default="")  
argParser.add_argument("-u", "--api", help="Hono device registry api url, example  https://my_hono_api/v1",
                       required=True)  
argParser.add_argument("-a", "--audience", help="Target audience (OAuth 2.0 Client), example 265883109532-md1u81cov3610ntcfnc7sfjp7vj6j6lm.apps.googleusercontent.com",
                       required=True)  
argParser.add_argument(
    "-r", "--region", help="Google Cloud Region. Valid regions are: {asia-east1,europe-west1,us-central1} Default is europe-west1.",  required=False, default="europe-west1")

argParser.add_argument("-t", "--tenant", help="Hono tenant ID.", required=True)
argParser.add_argument("-reg", "--registry", help="The Google IoT Core registry to migrate.", required=True)
argParser.add_argument('--migrate_gateways', action=argparse.BooleanOptionalAction)

def validate_args(args):
    if not args.project.strip():
        print("Project Id can not be empty.")
        exit(1)
    if not args.registry.strip():
        print("Registry can not be empty.")
        exit(1)
    elif not args.api.strip():
        print("Hono api url can not be empty.")
        exit(1)
    elif not args.audience.strip():
        print("GCP audience can not be empty.")
        exit(1)
    elif not args.region.strip():
        print("GCP region can not be empty.")
        exit(1)


def set_credential_global_variable(service_account_json):
    if service_account_json != "":
        os.environ[GOOGLE_CREDENTIAL_ENV_VARIABLE] = service_account_json


def create_devices(hono, tenant, devices, gateway_id: str = None):
    hono.create_hono_devices(tenant, devices, gateway_id)
     
    # Create credentials
    hono.create_hono_credentials(tenant, devices)
            
    # Create device config
    hono.create_hono_device_config(tenant, devices)
    
    

def start_migration(args):
     device_api = HonoDeviceApi(args.api, args.project)
     iot = IotCore(args.project, args.region)
     hono = HonoMigrator(args.api, TokenCreator, device_api, args.audience)
     
     # Create tenants
     registries = iot.list_registries()
          
     if args.registry not in [reg.id for reg in registries]:
         logging.error(f"IoT Core registry {args.registry} does not exist.")
         exit(1)
    
     hono.create_hono_tenant(args.tenant)
     
    
   
     gateway_ids = []
     gateway_device_ids = []
     gateways = iot.list_gateways( args.registry)
    
    
     if gateways and args.migrate_gateways:
        create_devices(hono, args.tenant, gateways)
        gateway_ids = [gateway.id for gateway in gateways]
        for gateway in gateways:
            
            # create devices from list using the via config
            gateway_devices = iot.list_gateway_devices(args.registry, gateway.id)
            gateway_device_ids = [device.id for device  in gateway_devices]
            create_devices(hono, args.tenant, gateway_devices, gateway.id)
        

     # Create devices
     all_devices = iot.list_devices(args.registry)
     devices_to_create = []
     for device in all_devices:
        if device.id in gateway_device_ids or device.id in gateway_ids:
            continue
        else:
            devices_to_create.append(device)
        

    
     logging.info(f"Found devices in registry {args.registry}: {[device.id for device in  devices_to_create]}")
     create_devices(hono, args.tenant, devices_to_create)
          

if __name__ == "__main__":
    args = argParser.parse_args()
    validate_args(args)
    set_credential_global_variable(args.key)
    try:
        start_migration(args)
    except Exception as ex:
        logging.error(ex)
    
