import logging
from requests.exceptions import ConnectionError
from misctypes import TimeUtil

class RetryingServiceProxyError(Exception):
    """Exception raised when RetryingServiceProxy hits an internal error"""
    pass

class MaxRetryError(Exception):
    """Exception raised when max retries have been attempted"""
    pass

class RetryingServiceProxy:
    """Context Manager class for contacting an external service"""

    @classmethod
    def configure(cls, svc,
                  min_retry_delay, max_retry_delay, retry_time_max,
                  time_util=None, max_retry_exception=MaxRetryError,
                  *temporary_exception_classes):
        """Configure the class

        :param svc: the service being proxied
        :type svc: object
        :param min_retry_delay: the minimum number of seconds to wait before
            retrying
        :type min_retry_delay: int
        :param max_retry_delay: the maximum number of seconds to wait before
            retrying; the actual retry starts at ``min_retry_delay`` and
            doubles with every temporary error until the ``max_retry_delay``
            is reached
        :type min_retry_delay: int
        :param retry_time_max: the maximum number of seconds to retry
            before raising a timeout error
        :type retry_time_max: int
        :param time_util: the TimeUtil class to use for returning the current
            time and for sleeping. Default is :class:`misctypes.TimeUtil`
        :type time_util: class, optional
        :param max_retry_exception: the Exception class to raise when all the
            ``retry_time_max`` time has been reached. Default is
            :class:`~retryingproxy.MaxRetryError`
        :type max_retry_exception: class, optional
        :param temporary_exception_classes: any remaining arguments are
            Exception classes that will be recognized as "temporary" errors
            that should cause a retry
        :type temporary_excpetion_classes: list of class, optional
        """
        cls.svc = svc
        cls.min_retry_delay = int(min_retry_delay)
        cls.max_retry_delay = int(max_retry_delay)
        cls.retry_time_max = int(retry_time_max)
        cls.time_util = TimeUtil() if time_util is None else time_util
        cls.max_retry_exception = max_retry_exception
        cls.retry_delay = None
        cls.retry_deadline = None
        tec = list(temporary_exception_classes)
        cls.temp_exception_classes = tec
        if ConnectionError not in tec:
            cls.temp_exception_classes.append(ConnectionError)
        cls.canonical_temp_exception_class = \
            cls.temp_exception_classes[0]
        cls.logger = logging.getLogger(__name__)
        
    def __enter__(self):
        cls = self.__class__
        if cls.svc is None:
            raise RetryingServiceProxyError("not configured")
        if cls.retry_delay is not None:
            cls.logger.debug("Sleeping " + str(self.retry_delay) + " sec")
            cls.time_util.sleep(self.retry_delay)
        return cls.svc

    def __exit__(self, exc_type, exc_value, exc_tb):
        cls = self.__class__
        if exc_type is None:
            cls.retry_delay = None
            cls.retry_deadline = None
            return False

        for tecls in self.temp_exception_classes:
            if exc_type is tecls:
                self._update_retry(exc_value)
                if exc_type is not self.canonical_temp_exception_class:
                    raise self.canonical_temp_exception_class() from exc_value
                break
        return False

    def _update_retry(self, exc):
        cls = self.__class__
        if cls.retry_delay is None:
            cls.retry_delay = int(self.min_retry_delay)
            cls.retry_deadline = \
                cls.time_util.future_time(int(cls.retry_time_max))
        else:
            if cls.time_util.now() > cls.retry_deadline:
                cls.retry_delay = None
                cls.retry_deadline = None
                raise cls.max_retry_exception() from exc
            cls.retry_delay *= 2
            if cls.retry_delay > cls.max_retry_delay:
                cls.retry_delay = cls.max_retry_delay


