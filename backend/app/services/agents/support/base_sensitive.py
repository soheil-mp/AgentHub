from typing import Dict, Any, Optional
from app.services.agents.base import BaseAgent
from datetime import datetime
import logging
import json
from cryptography.fernet import Fernet
from app.core.config import settings

logger = logging.getLogger(__name__)

class BaseSensitiveAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.encryption_key = Fernet(settings.ENCRYPTION_KEY)

    def encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt sensitive data."""
        json_data = json.dumps(data)
        return self.encryption_key.encrypt(json_data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt sensitive data."""
        decrypted_data = self.encryption_key.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())

    async def log_sensitive_operation(
        self,
        operation_type: str,
        user_id: str,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Log sensitive operations securely."""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "operation_type": operation_type,
                "user_id": user_id,
                "success": success,
                "error": error
            }
            logger.info(f"Sensitive operation logged: {json.dumps(log_entry)}")
        except Exception as e:
            logger.error(f"Failed to log sensitive operation: {str(e)}") 