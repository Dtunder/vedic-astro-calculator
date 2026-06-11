import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, Type, Tuple

logger = logging.getLogger(__name__)


def retry_with_fallback(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    fallback: Optional[Callable[..., Any]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    A decorator that retries a function upon specified exceptions
    with exponential backoff.
    If all retries fail and a fallback function is provided,
    it calls the fallback.

    Args:
        retries (int): Number of retries before giving up.
        delay (float): Initial delay between retries in seconds.
        backoff (float): Backoff multiplier.
        exceptions (Tuple[Type[Exception], ...]): Exceptions to catch.
        fallback (Optional[Callable[..., Any]]): Fallback function.

    Returns:
        Callable: The decorated function.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            func_name = getattr(func, "__name__", repr(func))
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt < retries:
                        logger.warning(
                            "Attempt %d/%d for %s failed with %s: %s. "
                            "Retrying in %.2fs...",
                            attempt + 1,
                            retries,
                            func_name,
                            type(e).__name__,
                            str(e),
                            current_delay,
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            "All %d attempts for %s failed. "
                            "Last error: %s: %s",
                            retries + 1,
                            func_name,
                            type(e).__name__,
                            str(e),
                        )
                        if fallback:
                            logger.info(
                                "Calling fallback for %s", func_name
                            )
                            return fallback(*args, **kwargs)
                        raise

        return wrapper

    return decorator
