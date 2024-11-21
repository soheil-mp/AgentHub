from typing import Dict, Any, Optional
from app.services.agents.base import BaseAgent
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseBookingAgent(BaseAgent):
    """Base class for all booking-related agents."""
    
    async def validate_booking_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate booking request data."""
        raise NotImplementedError("Subclasses must implement validate_booking_request")
    
    async def check_availability(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Check availability based on given criteria."""
        raise NotImplementedError("Subclasses must implement check_availability")
    
    async def create_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new booking."""
        raise NotImplementedError("Subclasses must implement create_booking")
    
    async def update_booking(self, booking_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing booking."""
        raise NotImplementedError("Subclasses must implement update_booking")
    
    async def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel a booking."""
        raise NotImplementedError("Subclasses must implement cancel_booking")
    
    async def get_booking_details(self, booking_id: str) -> Dict[str, Any]:
        """Get details of a specific booking."""
        raise NotImplementedError("Subclasses must implement get_booking_details")
    
    def _format_booking_response(self, booking_data: Dict[str, Any]) -> str:
        """Format booking data into a user-friendly response."""
        raise NotImplementedError("Subclasses must implement _format_booking_response")
    
    async def log_booking_operation(
        self,
        operation_type: str,
        booking_id: Optional[str],
        user_id: str,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Log booking operations."""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "operation_type": operation_type,
                "booking_id": booking_id,
                "user_id": user_id,
                "success": success,
                "error": error
            }
            logger.info(f"Booking operation logged: {log_entry}")
        except Exception as e:
            logger.error(f"Failed to log booking operation: {str(e)}") 