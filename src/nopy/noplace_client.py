import datetime
import enum
import http
import typing

import aiohttp

from . import profile


type _RequestMethod = typing.Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
type _KeyCase = typing.Literal["CAMEL", "SNAKE"]

class _RequestParams(typing.TypedDict):
    params: dict[str, str]
    data: dict[str, str] | bytes | typing.IO
    json: object
    headers: dict[str, str]
    cookies: dict[str, str]
    timeout: int


class NoplaceClientException(Exception):
    pass

class NoplaceClient:
    _API_BASE_URL = "https://api.nospace.app"
    _API_PREFIX = "/api/v1"
    _API_KEY = "AIzaSyAm02J4FCsnFw1-jdv7kGbqGwjtXOCpRUE"


    def __init__(
            self,
            phone_number: typing.Optional[str] = None,
            id_token: typing.Optional[str] = None,
            refresh_token: typing.Optional[str] = None
        ):
        self.phone_number = phone_number
        self.id_token = id_token
        self.refresh_token = refresh_token
        self.profile_id = None

    async def get_tokens_from_resp(self, resp: aiohttp.ClientResponse, key_case: _KeyCase = "CAMEL") -> tuple[str, str, int]:
        match key_case:
            case "SNAKE":
                id_token_key = "id_token"
                refresh_token_key = "refresh_token"
                expires_in_key = "expires_in"
            case _:
                id_token_key = "idToken"
                refresh_token_key = "refreshToken"
                expires_in_key = "expiresIn"

        resp_json = await resp.json()
        try:
            self.id_token = resp_json[id_token_key]
            self.refresh_token = resp_json[refresh_token_key]
            expires_in = int(resp_json[expires_in_key])
            return self.id_token, self.refresh_token, expires_in
        except KeyError as e:
            raise NoplaceClientException(f"{e} not in response:\n{resp_json}")

    async def send_otp(self) -> str:
        resp = await self._api_post("/auth/otp", json={"phoneNumber": self.phone_number})
        if "requestId" in resp:
            return resp["requestId"]
        raise NoplaceClientException(f"requestId not in response:\n{resp}")

    async def verify_otp(self, request_id: str, otp: str) -> str:
        resp = await self._api_post("/auth/otp/verify", json={"requestId": request_id, "otp": otp})
        if "accessToken" in resp:
            return resp["accessToken"]
        raise NoplaceClientException(f"accessToken not in response:\n{resp}")

    async def sign_in(self, access_token) -> tuple[str, str, int]:
        async with aiohttp.ClientSession("https://identitytoolkit.googleapis.com") as session:
            async with session.post(
                "/v1/accounts:signInWithCustomToken",
                params={"key": self._API_KEY},
                json={"token": access_token, "returnSecureToken": True}
            ) as resp:
                if resp.ok:
                    return await self.get_tokens_from_resp(resp)
                resp_text = await resp.text()
                raise NoplaceClientException(f"Request error:\n{resp_text}")

    async def refresh_id_token(self) -> tuple[str, str, int]:
        if self.refresh_token is None:
            raise NoplaceClientException("Client has no refresh token")
        async with aiohttp.ClientSession("https://securetoken.googleapis.com") as session:
            async with session.post(
                "/v1/token",
                params={"key": self._API_KEY},
                json={"grant_type": "refresh_token", "refresh_token": self.refresh_token}
            ) as resp:
                if resp.ok:
                    return await self.get_tokens_from_resp(resp, key_case="SNAKE")
                resp_text = await resp.text()
                raise NoplaceClientException(f"Request error:\n{resp_text}")

    async def get_profile(self, profile_id=""):
        if profile_id == "":
            if self.profile_id is None:
                resp = await self._api_get("/profiles")
                self.profile_id = resp[0]["profile_id"]
            profile_id = self.profile_id
        return profile.Profile.from_json(await self._api_get(f"/profiles/{profile_id}"))

    async def _api_request(self, method: _RequestMethod, endpoint: str, **kwargs: _RequestParams) -> aiohttp.ClientResponse:
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        if self.id_token is not None:
            kwargs["headers"]["Authorization"] = f"Bearer {self.id_token}"

        async with aiohttp.ClientSession(self._API_BASE_URL) as session:
            async with session.request(method, f"{self._API_PREFIX}{endpoint}", **kwargs) as resp:
                if resp.ok:
                    return await resp.json()
                resp_text = await resp.text()
                raise NoplaceClientException(f"Request error:\n{resp_text}")

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

