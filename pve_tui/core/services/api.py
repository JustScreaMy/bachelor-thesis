import aiohttp
from contextlib import asynccontextmanager
from typing import Self, AsyncIterator, AsyncContextManager

from .. import models

class ProxmoxClient:
    proxmox_base_url: str
    auth_token_id: str
    auth_token: str
    _session: aiohttp.ClientSession | None

    def __init__(
            self, proxmox_base_url: str, auth_token_id: str, auth_token: str
    ) -> None:
        self.proxmox_base_url = proxmox_base_url
        self.auth_token_id = auth_token_id
        self.auth_token = auth_token
        self._session = None

    @classmethod
    def from_config(
            cls, application_config: models.ApplicationConfig, context: str = ""
    ) -> Self:
        """Creates ProxmoxClient from ApplicationConfig."""
        if context:
            try:
                server_config = application_config.contexts[context]
            except KeyError:
                raise ValueError(f"Context '{context}' not found.")
        else:
            try:
                # Get the first context alphabetically
                first_context = sorted(application_config.contexts.keys()).pop(0)
                server_config = application_config.contexts[first_context]
            except (IndexError, KeyError):
                raise ValueError("No valid context found in application configuration.")

        return cls(
            proxmox_base_url=server_config.base_url,
            auth_token_id=server_config.token_id,
            auth_token=server_config.token,
        )

    @property
    def base_url(self) -> str:
        if not self.proxmox_base_url.endswith("/api2/json"):
            return f"{self.proxmox_base_url}/api2/json"
        return self.proxmox_base_url

    async def get_session(self) -> aiohttp.ClientSession:
        """
        Returns the existing session or creates a new one if it doesn't exist 
        or is closed.
        """
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=False)
            headers = {
                "Authorization": f"PVEAPIToken={self.auth_token_id}={self.auth_token}"
            }
            self._session = aiohttp.ClientSession(connector=connector, headers=headers)

        return self._session

    async def close(self) -> None:
        """Closes the underlying ClientSession."""
        if self._session and not self._session.closed:
            await self._session.close()

    def request(
            self, endpoint: str, method: str = "GET", **kwargs
    ) -> AsyncContextManager[aiohttp.ClientResponse]:
        @asynccontextmanager
        async def _request() -> AsyncIterator[aiohttp.ClientResponse]:
            if not endpoint.startswith("/"):
                fixed_endpoint = f"/{endpoint}"
            else:
                fixed_endpoint = endpoint

            url = f"{self.base_url}{fixed_endpoint}"

            # Get the shared session
            session = await self.get_session()

            # We assume the caller handles the response lifecycle
            # The session remains open for subsequent requests
            try:
                async with session.request(method, url, **kwargs) as resp:
                    yield resp
            except aiohttp.ClientError as e:
                # Optional: Log error here
                raise e

        return _request()

    async def is_healthy(self) -> bool:
        try:
            async with self.request("/version") as resp:
                return resp.status == 200
        except Exception:
            return False