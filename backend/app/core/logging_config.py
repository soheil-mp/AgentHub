import logging
import sys
from app.core.config import settings

# Configure root logger
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create loggers for different components
mongodb_logger = logging.getLogger('app.services.database')
redis_logger = logging.getLogger('app.services.cache')
api_logger = logging.getLogger('app.api')
agent_logger = logging.getLogger('app.services.agents')

# Set levels
mongodb_logger.setLevel(settings.LOG_LEVEL)
redis_logger.setLevel(settings.LOG_LEVEL)
api_logger.setLevel(settings.LOG_LEVEL)
agent_logger.setLevel(settings.LOG_LEVEL) 