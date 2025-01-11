"""
original code from https://github.com/lupohan44/PyCookieCloud
Author: lupohan44
modified by: Well404
modified date: 2025-1-11
"""

import base64
import hashlib
import json
from hashlib import md5
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urljoin

import httpx
from Cryptodome import Random
from Cryptodome.Cipher import AES


def bytes_to_key(data: bytes, salt: bytes, output: int = 48) -> bytes:
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]


class PyCookieCloud:
    def __init__(self, url: str, uuid: str, password: str) -> None:
        self.url: str = url
        self.uuid: str = uuid
        self.password: str = password
        self.client = httpx.AsyncClient()

    def _get_the_key(self) -> str:
        """
        Get the key used to encrypt and decrypt data.

        :return: the key.
        """
        md5 = hashlib.md5()
        md5.update((self.uuid + "-" + self.password).encode("utf-8"))
        return md5.hexdigest()[:16]

    def _decrypt_data(self, encrypted_data: str) -> dict[str, Any]:
        encrypted_bytes = base64.b64decode(encrypted_data)
        assert encrypted_bytes[0:8] == b"Salted__"
        key_iv = bytes_to_key(self._get_the_key().encode("utf-8"), encrypted_bytes[8:16], 32 + 16)
        data = AES.new(key_iv[:32], AES.MODE_CBC, key_iv[32:]).decrypt(encrypted_bytes[16:])
        decrypted_data = data[: -(data[-1] if isinstance(data[-1], int) else ord(data[-1]))].decode("utf-8")
        decrypted_data = json.loads(decrypted_data)
        if "cookie_data" not in decrypted_data:
            raise ValueError(f"Decryption failed, raw data: \n{decrypted_data}")
        decrypted_data = decrypted_data["cookie_data"]
        bilibili_cookie = decrypted_data.get("bilibili.com", None) or decrypted_data.get("www.bilibili.com", None)
        if bilibili_cookie:
            return {c["name"]: c["value"] for c in bilibili_cookie}
        raise ValueError(f"Decryption failed, raw data: \n{decrypted_data}")

    async def get_cookie(self) -> dict[str, str | int | float | bool]:
        path = str(PurePosixPath("/get/", self.uuid))
        cookie_cloud_request = await self.client.get(urljoin(self.url, path))
        cookie_cloud_request.raise_for_status()
        cookie_cloud_response = cookie_cloud_request.json()
        return self._decrypt_data(cookie_cloud_response["encrypted"])

    def get_cookie_sync(self) -> dict[str, str | int | float | bool]:
        path = str(PurePosixPath("/get/", self.uuid))
        cookie_cloud_request = httpx.get(urljoin(self.url, path))
        cookie_cloud_request.raise_for_status()
        cookie_cloud_response = cookie_cloud_request.json()
        return self._decrypt_data(cookie_cloud_response["encrypted"])

    async def update_cookie(self, cookie: dict[str, Any]) -> None:
        """
        Update cookie data to CookieCloud.

        :param cookie: cookie value to update, if this cookie does not contain 'cookie_data' key, it will be added into 'cookie_data'.
        :return: if update success, return True, else return False.
        """
        if "cookie_data" not in cookie:
            cookie = {"cookie_data": cookie}
        message = json.dumps(cookie).encode("utf-8")
        salt = Random.new().read(8)
        key_iv = bytes_to_key(self._get_the_key().encode("utf-8"), salt, 32 + 16)
        length = 16 - (len(message) % 16)
        message = message + (chr(length) * length).encode()
        encrypted_data = base64.b64encode(
            b"Salted__" + salt + AES.new(key_iv[:32], AES.MODE_CBC, key_iv[32:]).encrypt(message)
        ).decode("utf-8")
        cookie_cloud_request = await self.client.post(
            urljoin(self.url, "/update"), data={"uuid": self.uuid, "encrypted": encrypted_data}
        )
        cookie_cloud_request.raise_for_status()
        if cookie_cloud_request.json()["action"] != "done":
            raise ValueError(f"Update failed, raw data: \n{cookie_cloud_request.json()}")
