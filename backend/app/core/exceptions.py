"""
自定义异常类
统一异常处理，便于错误追踪和用户提示
"""


class AppException(Exception):
    def __init__(self, code: int = 500, message: str = "服务器内部错误"):
        self.code = code
        self.message = message
        super().__init__(message)


class AuthenticationError(AppException):
    def __init__(self, message: str = "认证失败"):
        super().__init__(code=401, message=message)


class AuthorizationError(AppException):
    def __init__(self, message: str = "权限不足"):
        super().__init__(code=403, message=message)


class NotFoundError(AppException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=404, message=message)


class ValidationError(AppException):
    def __init__(self, message: str = "数据验证失败"):
        super().__init__(code=400, message=message)


class ConflictError(AppException):
    def __init__(self, message: str = "资源冲突"):
        super().__init__(code=409, message=message)


class AIError(AppException):
    def __init__(self, message: str = "AI服务调用失败"):
        super().__init__(code=503, message=message)