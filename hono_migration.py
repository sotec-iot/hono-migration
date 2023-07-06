
import logging
from typing import List
from api import HonoDeviceApi
from gcp_token import TokenCreator
from google.cloud.iot_v1.types.resources import Device

class HonoMigrator:
     def __init__(self, hono_api_url: str, token_manager: TokenCreator, device_api: HonoDeviceApi, oauth_client: str):
          self.api_url = hono_api_url
          self.token_manager = token_manager
          self.device_api = device_api
          self.oauth_client = oauth_client
      
      
      
     def __log_response(self, resource_type, resource_id, result):
          if result.ok:     
               logging.info(f"{resource_type} {resource_id} was created successfully.")
          elif result.status_code == 409:
               logging.info(f"{resource_type} {resource_id} already exist.")
          else:
               logging.error(f"{resource_type} {resource_id} can not be created. API response code {result.status_code}")
      
      
          
     def create_hono_tenant(self, tenant: str):
          """ Create hono tenant"""
          
          token = self.token_manager.create_token(self.oauth_client)
          
          try:
               result =  self.device_api.create_tenant(tenant, token)
               self.__log_response("Tenant", tenant, result)  
          except Exception as ex:
               logging.error(
                    f"Tenant {tenant} can not be created. Cause {ex}")

                     
                     
     def create_hono_devices(self, registry: str, devices: List[Device], gateway_id: str = None):
          """ Create hono devices. """
          
          token = self.token_manager.create_token(self.oauth_client)
          logging.info(f"Creating devices for tenant {registry}")
          for device in devices:
               try:
                    result =  self.device_api.create_device(registry, device, token, gateway_id)
                    self.__log_response("Device", device.id, result)  
               except Exception as ex:
                     logging.error(f"Device {device.id} can not be created. Cause {ex}")


     def create_hono_device_config(self, registry: str, devices: List[Device]):
          """ Create hono devices config. """
          
          token = self.token_manager.create_token(self.oauth_client)
          for device in devices:
               if not device.config or not device.config.binary_data:
                    continue
               logging.info(f"Creating device config for device {device.id} tenant {registry}")
               try:
                    result =  self.device_api.create_device_config(registry, device, token)
                    if result is None:
                         logging.info(f"Config for device {device.id} is empty.")
                    elif result.ok:
                         logging.info(f"Config for device {device.id} was created successfully.")
                    else:
                         logging.error(f"Config for device {device.id} can not be created. API response code {result.status_code}")
               except UnicodeDecodeError as ex:
                   logging.warning(
                       f"Config for device {device.id} is empty or not valid. Cause {ex}")
               except Exception as ex:
                   logging.error(
                       f"Config for device {device.id} can not be created. Cause {ex}")
                     
                     
     def create_hono_credentials(self, registry: str, devices: List[Device]):
               """ Create hono device credentials. """
               
               token = self.token_manager.create_token(self.oauth_client)
               logging.info(f"Creating Devices Credentials for tenant {registry}")
               for device in devices:
                   if "credentials" not in str(vars(device)):
                       continue
                   try:
                         result =  self.device_api.create_credential(registry, device, token)
                         self.__log_response("Credential for device", device.id, result)                        
                   except Exception as ex:
                         logging.error(f"Credential for device {device.id} can not be created. Cause {ex}")
                         
                         

    