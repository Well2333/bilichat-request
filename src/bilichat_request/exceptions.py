class ResponseCodeError(Exception):
    """请求返回 code 不为 0"""

    def __init__(self, code: int, msg: str, data: dict) -> None:
        self.code = code
        self.msg = msg
        self.data = data

    def __repr__(self) -> str:
        return f"错误码: {self.code}, 信息: {self.msg}"

    def __str__(self) -> str:
        return self.__repr__()


class AuthParamError(Exception):
    """缺少必要鉴权参数"""

    def __init__(self, *params: str) -> None:
        self.params = params

    def __repr__(self) -> str:
        return f"缺少鉴权参数 {', '.join(self.params)}"

    def __str__(self) -> str:
        return self.__repr__()


class AuthTypeError(Exception):
    """鉴权类型错误"""

    def __init__(self, auth_type: str) -> None:
        self.auth_type = auth_type

    def __repr__(self) -> str:
        return f"'{self.auth_type}' 是当前不支持的鉴权类型"

    def __str__(self) -> str:
        return self.__repr__()


class GrpcError(Exception):
    """RPC 错误"""

    def __init__(self, code: int, msg: str) -> None:
        self.code = code
        self.msg = msg

    def __repr__(self) -> str:
        return f"错误码: {self.code}, 信息: {self.msg}"

    def __str__(self) -> str:
        return self.__repr__()


class ProssesError(Exception):
    """处理时的异常, 通常由于环境错误导致"""

    def __init__(self, message: object) -> None:
        self.message = message


class AbortError(Exception):
    """通常情况下是由外部因素 (如风控) 导致, 不影响其余任务执行的异常"""

    def __init__(self, message: object) -> None:
        self.message = message


class CaptchaAbortError(AbortError):
    """由于风控导致需要验证码的异常"""

    def __init__(self, message: object) -> None:
        self.message = message


class NotFindAbortError(AbortError):
    """未找到指定资源的异常"""

    def __init__(self, message: object) -> None:
        self.message = message
