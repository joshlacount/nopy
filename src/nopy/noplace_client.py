import enum
import http
import typing

import aiohttp


type _RequestMethod = typing.Literal["GET", "POST", "PUT", "PATCH", "DELETE"]

class _RequestParams(typing.TypedDict):
    params: dict[str, str]
    data: dict[str, str] | bytes | typing.IO
    json: object
    headers: dict[str, str]
    cookies: dict[str, str]
    timeout: int


class NoplaceClientException(Exception):
    def __init__(self, msg: str, resp: aiohttp.ClientResponse):
        super().__init__(msg)
        self.msg = msg
        self.resp = resp


class NoplaceClient:
    _API_BASE_URL = "https://api.nospace.app"
    _API_PREFIX = "/api/v1"
    _API_KEY = "AIzaSyAm02J4FCsnFw1-jdv7kGbqGwjtXOCpRUE"


    def __init__(self, phone_number: str):
        self.phone_number = phone_number

        self.id_token = None

    async def send_otp(self) -> str:
        resp = await self._api_post("/auth/otp", json={"phoneNumber": self.phone_number})
        if resp.ok:
            resp_json = await resp.json()
            if "requestId" in resp_json:
                return resp_json["requestId"]
            raise NoplaceClientException("requestId not in response JSON", resp)
        raise NoplaceClientException("Request error", resp)

    async def verify_otp(self, request_id: str, otp: str) -> str:
        resp = await self._api_post("/auth/otp/verify", json={"requestId": request_id, "otp": otp})
        if resp.ok:
            resp_json = await resp.json()
            if "accessToken" in resp_json:
                return resp_json["accessToken"]
            raise NoplaceClientException("accessToken not in response JSON", resp)
        raise NoplaceClientException("Request error", resp)

    async def sign_in(self, access_token):
        async with aiohttp.ClientSession("https://identitytoolkit.googleapis.com") as session:
            async with session.post(
                "/v1/accounts:signInWithCustomToken",
                params={"key": self._API_KEY},
                json={"token": access_token, "returnSecureToken": True}
            ) as resp:
                if resp.ok:
                    resp_json = await resp.json()
                    try:
                        self.id_token = resp_json["idToken"]
                        refresh_token = resp_json["refreshToken"]
                        expires_in = resp_json["expiresIn"]
                    except KeyError as e:
                        raise NoplaceClientException(str(e), resp)
                    return self.id_token, refresh_token, expires_in
                raise NoplaceClientException("Request error", resp)

    async def _api_request(self, method: _RequestMethod, endpoint: str, **kwargs: _RequestParams) -> aiohttp.ClientResponse:
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        if self.id_token is not None:
            kwargs["headers"]["Authorization"] = f"Bearer {self.id_token}"

        async with aiohttp.ClientSession(self._API_BASE_URL) as session:
            return await session.request(method, f"{self._API_PREFIX}{endpoint}", **kwargs)

    async def _api_get(self, endpoint: str, **kwargs: _RequestParams) -> aiohttp.ClientResponse:
        return await self._api_request("GET", endpoint, **kwargs)

    async def _api_post(self, endpoint: str, **kwargs: _RequestParams) -> aiohttp.ClientResponse:
        return await self._api_request("POST", endpoint, **kwargs)

    async def _api_put(self, endpoint: str, **kwargs: _RequestParams) -> aiohttp.ClientResponse:
        return await self._api_request("PUT", endpoint, **kwargs)

    async def _api_patch(self, endpoint: str, **kwargs: _RequestParams) -> aiohttp.ClientResponse:
        return await self._api_requests("PATCH", endpoint, **kwargs)

    async def _api_delete(self, endpoint: str, **kwargs: _RequestParams) -> aiohttp.ClientResponse:
        return await self._api_requests("DELETE", endpoint, **kwargs)

