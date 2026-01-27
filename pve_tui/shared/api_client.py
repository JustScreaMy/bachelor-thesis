import asyncio
from typing import Self

import aiohttp

from pve_tui.shared import models


class APIClient:
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
        """Creates APIClient from ApplicationConfig. If no context is provided, the alphabetically first one is used."""
        if context:
            try:
                server_config = application_config.contexts[context]
            except KeyError:
                raise ValueError(
                    f"Context '{context}' not found in application configuration."
                )
        else:
            first_context = ""
            try:
                first_context = sorted(application_config.contexts.keys()).pop(0)
                server_config = application_config.contexts[first_context]
            except IndexError:
                raise ValueError("No contexts found in application configuration.")
            except KeyError:
                raise ValueError(
                    f"Context '{first_context}' not found in application configuration."
                )

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
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=False)
            headers = {
                "Authorization": f"PVEAPIToken={self.auth_token_id}={self.auth_token}"
            }
            self._session = aiohttp.ClientSession(connector=connector, headers=headers)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(
        self, endpoint: str, method: str = "GET", **kwargs
    ) -> aiohttp.ClientResponse:
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        url = f"{self.base_url}{endpoint}"
        session = await self.get_session()
        return await session.request(method, url, **kwargs)

    async def is_healthy(self) -> bool:
        try:
            async with await self.request("/version") as resp:
                return resp.status == 200
        except Exception:
            return False

    async def get_nodes(self) -> list[str]:
        async with await self.request("/nodes") as response:
            response.raise_for_status()
            data = await response.json()
            nodes = [node["node"] for node in data.get("data", [])]
            return nodes

    async def get_servers_brief(self) -> list[models.ServerBrief]:
        nodes = await self.get_nodes()
        servers = []

        async def fetch_node_vms(node_name: str) -> list[dict]:
            async with await self.request(f"/nodes/{node_name}/qemu") as res:
                res.raise_for_status()
                data = await res.json()
                return data.get("data", [])

        results = await asyncio.gather(
            *(fetch_node_vms(node) for node in nodes), return_exceptions=True
        )

        for result in results:
            if isinstance(result, Exception):
                continue

            for server in result:
                status_value = server.get("status", "stopped")
                try:
                    status = models.ServerStatus(status_value)
                except ValueError:
                    status = models.ServerStatus.Stopped

                servers.append(
                    models.ServerBrief(
                        server_id=server.get("vmid", 0),
                        name=server.get("name", ""),
                        status=status,
                        cpus=server.get("cpus", 0),
                        cpu_usage=server.get("cpu", 0),
                        memory=server.get("maxmem", 0),
                        memory_used=server.get("mem", 0),
                        uptime=server.get("uptime", 0),
                    )
                )
        return servers
