import structlog
import logging
import sys

# Configure structlog for structured, JSON-formatted logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),              # Add ISO timestamp to each log
        structlog.stdlib.add_log_level,                           # Include log level (e.g., info, error)
        structlog.stdlib.add_logger_name,                         # Include logger name
        structlog.stdlib.PositionalArgumentsFormatter(),          # Handle positional args in log calls
        structlog.processors.StackInfoRenderer(),                 # Add stack info if available
        structlog.processors.format_exc_info,                     # Format exception info if present
        structlog.processors.JSONRenderer()                       # Render log entries as JSON
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Set up Python's standard logging to output messages compatible with structlog
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

# Create a logger instance to be reused across the application
logger = structlog.get_logger()
