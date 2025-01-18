import logging
import time

from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class RetryOnOperationalErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_retries = getattr(settings, "DATABASE_RETRY_MAX_RETRIES", 3)
        self.base_delay = getattr(settings, "DATABASE_RETRY_BASE_DELAY", 0.5)

    def __call__(self, request):
        retries = 0
        delay = self.base_delay

        while retries < self.max_retries:
            try:
                with connections["default"].cursor() as cursor:
                    cursor.execute("SELECT 1")
                response = self.get_response(request)
                return response

            except OperationalError as e:
                retries += 1
                logger.warning(
                    f"OperationalError encountered, retrying ({retries}/{self.max_retries})...: {e}"
                )
                if retries >= self.max_retries:
                    raise e
                time.sleep(delay)
                delay *= 2
        return self.get_response(request)
