from google.oauth2 import service_account
import google.oauth2.id_token
import google.auth.transport.requests
import logging

class TokenCreator:

    def create_token(client_id: str) -> str:
          """Creates a new token for the given client id"""
 
          request = google.auth.transport.requests.Request()
          try:
               credentials = google.oauth2.id_token.fetch_id_token_credentials(client_id, request=request)
               credentials.refresh(request)
          except Exception as e:
               logging.error(f"Failed to create token for client id {client_id}, cause: {e}")
               exit(1)
                  
          return credentials.token
