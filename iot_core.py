import logging
from typing import List
from google.cloud import iot_v1
from google.protobuf import field_mask_pb2 as gp_field_mask
from google.cloud.iot_v1.types.resources import Device

class IotCore:
     def __init__(self, project_id: str, cloud_region: str):
          self.project_id = project_id
          self.cloud_region = cloud_region
          
     def list_registries(self) -> List[object]:
          """List all registries in the project."""

          client = iot_v1.DeviceManagerClient()
          parent = f"projects/{self.project_id}/locations/{self.cloud_region}"

          registries = list(client.list_device_registries(
               request={"parent": parent}))

          return registries
     
   
     def list_devices(self, registry_id: str) -> List[Device]:
          """List all devices in the registry."""

          client = iot_v1.DeviceManagerClient()
          registry_path = client.registry_path(self.project_id, self.cloud_region, registry_id)

        
          field_mask = gp_field_mask.FieldMask(
               paths=[
                    "id",
                    "name",
                    "credentials",
                    "blocked",
                    "config",
                    "gateway_config",
               ]
          )

          devices = list(
               client.list_devices(request={"parent": registry_path, "field_mask": field_mask})
          )

          return devices
     
     
     
     def list_gateways(self, registry_id: str) -> List[Device]:
          client = iot_v1.DeviceManagerClient()

          path = client.registry_path(self.project_id, self.cloud_region, registry_id)
          mask = gp_field_mask.FieldMask(
               paths=[
                    "id",
                    "name",
                    "credentials",
                    "blocked",
                    "config",
                    "gateway_config",
               ]
          )
          devices = list(client.list_devices(request={"parent": path, "field_mask": mask}))

          gateways = []
          for device in devices:
               if device.gateway_config is not None:
                    if device.gateway_config.gateway_type == 1:
                         gateways.append(device)
                   
          return gateways
                         
     def list_gateway_devices(self, registry_id: str, gateway_id: str):
          client = iot_v1.DeviceManagerClient()

          path = client.registry_path(self.project_id, self.cloud_region, registry_id)
          mask = gp_field_mask.FieldMask(
               paths=[
                    "id",
                    "name",
                    "credentials",
                    "blocked",
                    "config",
                    "gateway_config",
               ]
          )
          
          devices = list(
          client.list_devices(
               request={"parent": path, "field_mask": mask, "gateway_list_options": {"associations_gateway_id": gateway_id,}})
          )

          if not devices:
               logging.warning("No devices bound to gateway {}".format(gateway_id))
          
          return devices
         