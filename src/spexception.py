
class ServiceProviderRequestFailed(Exception):
    """Exception raised when a request could not be satisfied"""
    pass

class ServiceProviderError(Exception):
    """Exception raised when the Service Provider hits an internal error"""
    pass

class ServiceProviderTimeout(Exception):
    """Exception raised when get_packets() request times out"""
    pass

class ServiceProviderTemporaryError(Exception):
    """Exception raised when an operation fails but should be retried"""
    pass
