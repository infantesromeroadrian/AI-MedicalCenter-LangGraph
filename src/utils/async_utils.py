import asyncio
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def async_route(f):
    """
    Decorator to handle asynchronous Flask routes.
    Properly manages the asyncio event loop to prevent "Event loop is closed" errors.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # If there's no event loop in the current thread, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async function and return its result
            return loop.run_until_complete(f(*args, **kwargs))
        except Exception as e:
            logger.error(f"Error in async route: {str(e)}")
            raise
    
    return wrapper 