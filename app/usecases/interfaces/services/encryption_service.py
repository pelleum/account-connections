from abc import ABC, abstractmethod


class IEncryptionService(ABC):
    @abstractmethod
    async def encrypt(self, secret: str) -> str:
        """Returns encrypted secret"""

    @abstractmethod
    async def decrypt(self, encrypted_secret: str) -> str:
        """Returns decrypted secret"""
