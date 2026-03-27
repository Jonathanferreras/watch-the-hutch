import os
import time
import jwt

class AuthService:
    def __init__(self):
        self.secret = os.getenv("ADMIN_SECRET_KEY", "")
        self.algorithm = "HS256"

    def token_response(self, token: str):
        return {
            "access_token": token
        }

    def sign_jwt(self, user_id: int):
        payload = {
            "user_id": user_id,
            "expires": time.time() + 600
        }
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)

        return self.token_response(token)

    def decode_jwt(self, token:str):
        try:
            decoded_token = jwt.decode(token, self.secret, algorithms=[self.algorithm])

            return decoded_token if decoded_token["expires"] >= time.time() else None
        except Exception:
            return None
        
    def verify_jwt(self, token:str):
        try:
            payload = self.decode_jwt(token)
        except Exception:
            payload = None

        return True if payload else False
