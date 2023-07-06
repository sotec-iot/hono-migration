import base64
import requests
import json
from requests import Response
import logging
from google.cloud.iot_v1.types.resources import Device
from google.protobuf.json_format import MessageToDict
import urllib3

urllib3.disable_warnings()


class HonoDeviceApi:
    def __init__(self, api_url: str, project_id: str):
        self.tenants_url = f"{api_url}/tenants"
        self.devices_url = f"{api_url}/devices"
        self.credentials_url = f"{api_url}/credentials"
        self.configs_url = f"{api_url}/configs"
        self.project_id = project_id

    def __get_payload_pk(self, key: str, device: Device, algorithm: str):
        key = key.replace("-----BEGIN PUBLIC KEY-----", "")
        key = key.replace("-----END PUBLIC KEY-----", "")
        key = key.replace("\n", "")
        key = key.replace("\r", "")

        if device.credentials is not None and len(device.credentials) > 0 and device.credentials[0].expiration_time and device.credentials[0].expiration_time.timestamp() != 0:
            return json.dumps([{
                "type": "rpk",
                "auth-id": device.id,
                "secrets": [
                    {
                        "algorithm": algorithm,
                        "key": key,
                        "not-after": device.credentials[0].expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                ]
            }])

        else:
            return json.dumps([{
                "type": "rpk",
                "auth-id": device.id,
                "secrets": [
                    {
                        "algorithm": algorithm,
                        "key": key

                    }
                ]
            }])

    def __get_payload_cert(self, key, device):
        key = key.replace("-----BEGIN CERTIFICATE-----", "")
        key = key.replace("-----END CERTIFICATE-----", "")
        key = key.replace("\n", "")
        key = key.replace("\r", "")

        return json.dumps([{
            "type": "rpk",
            "auth-id": device.id,
            "secrets": [
                {
                    "cert": key
                }
            ]
        }])

    def __get__header(self, token):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    def create_tenant(self, tenant_id: str, token: str) -> Response:
        """ Create a new tenant. """

        url = f"{self.tenants_url}/{tenant_id}"

        payload = json.dumps({
            "ext": {
                "messaging-type": "pubsub",
                "projectId": self.project_id
            }
        })

        return requests.request("POST", url, headers=self.__get__header(token), data=payload, verify=False)

    def create_device(self, tenant_id: str,  device: Device, token: str, gateway_id: str) -> Response:
        """ Create a new device. """

        url = f"{self.devices_url}/{tenant_id}/{device.id}"
        payload = {}
        
        if gateway_id is not None:
            payload = json.dumps({
                "via": [
                    gateway_id,
                ],
            })

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        return requests.request("POST", url, headers=headers, data=payload, verify=False)
    

    def create_device_config(self, tenant_id: str,  device: Device, token: str) -> Response:
        """ Create configs for a device. """

        url = f"{self.configs_url}/{tenant_id}/{device.id}"

        config_str = base64.b64encode(device.config.binary_data).decode()

        payload = json.dumps({
            "binaryData": config_str
        })

        return requests.request("POST", url, headers=self.__get__header(token), data=payload, verify=False)

    def create_credential(self, tenant_id: str, device: Device, token: str) -> Response:
        """ Create device credentials. """

        url = f"{self.credentials_url}/{tenant_id}/{device.id}"
        public_key = MessageToDict(device.credentials.pb[0])["publicKey"]

        key = public_key["key"]
        key_format = public_key["format"]
        is_cert = False

        if "X509" in key_format:
            is_cert = True
        else:
            if "ES" in key_format:
                algorithm = "EC"
            elif "RS" in key_format:
                algorithm = "RSA"
            else:
                logging.error(
                    f"Can not create credentials for device {device.id}, cause: unsupported credentials algorithm {key_format}")
                return None

        if is_cert:
            payload = self.__get_payload_cert(key, device)
        else:
            payload = self.__get_payload_pk(key, device, algorithm)

        return requests.request("PUT", url, headers=self.__get__header(token), data=payload, verify=False)
