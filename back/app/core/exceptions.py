from fastapi import status


class BadRequestException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail="Bad Request"):
        self.detail = detail


class InternalServerException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail="Internal Server Error"):
        self.detail = detail
