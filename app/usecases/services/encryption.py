from base64 import b64decode, b64encode

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from app.settings import settings
from app.usecases.interfaces.services.encryption_service import IEncryptionService


class EncryptionService(IEncryptionService):
    def __init__(self):
        pass

    async def encrypt(self, secret: str) -> str:
        """Returns encrypted secret"""

        encryption_secret_key = b64decode(settings.encryption_secret_key.encode())
        cipher = AES.new(encryption_secret_key, AES.MODE_CBC)
        iv_string = b64encode(cipher.iv).decode("utf-8")
        encypted_bytes = cipher.encrypt(pad(secret.encode(), AES.block_size))
        enrypted_secret_string = b64encode(encypted_bytes).decode("utf-8")
        return enrypted_secret_string + iv_string

    async def decrypt(self, encrypted_secret: str) -> str:
        """Returns decrypted secret"""

        encryption_secret_key = b64decode(settings.encryption_secret_key.encode())
        iv = b64decode(encrypted_secret[-24:].encode())
        encrypted_data = b64decode(encrypted_secret[:-24])
        cipher = AES.new(encryption_secret_key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size).decode(
            "utf-8"
        )
        return decrypted_data
