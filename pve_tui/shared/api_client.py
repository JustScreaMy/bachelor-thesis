from typing import Self

import urllib3
from requests import Session, Response
from urllib3.exceptions import SecurityWarning

from pve_tui.shared import models

# Most of Proxmox VE instances use self-signed certificates, so we disable warnings here.
urllib3.disable_warnings(SecurityWarning)


class APIClient:
    proxmox_base_url: str

    auth_token_id: str
    auth_token: str
    session: Session

    def __init__(
            self, proxmox_base_url: str, auth_token_id: str, auth_token: str
    ) -> None:
        self.proxmox_base_url = proxmox_base_url
        self.auth_token_id = auth_token_id
        self.auth_token = auth_token

        self.session = Session()
        self.session.verify = False
        self.session.headers.update(
            {"Authorization": f"PVEAPIToken={self.auth_token_id}={self.auth_token}"}
        )

    @classmethod
    def from_config(cls, application_config: models.ApplicationConfig, context: str = "") -> Self:
        """Creates APIClient from ApplicationConfig. If no context is provided, the alphabetically first one is used."""
        if context:
            try:
                server_config = application_config.contexts[context]
            except KeyError:
                raise ValueError(f"Context '{context}' not found in application configuration.")
        else:
            first_context = ""
            try:
                first_context = sorted(application_config.contexts.keys()).pop(0)
                server_config = application_config.contexts[first_context]
            except IndexError as ex:
                raise ValueError("No contexts found in application configuration.")
            except KeyError as ex:
                raise ValueError(f"Context '{first_context}' not found in application configuration.")

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

    def request(self, endpoint: str, method: str = "GET", **kwargs) -> Response:
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        url = f"{self.base_url}{endpoint}"
        return self.session.request(method, url, **kwargs)

    def is_healthy(self) -> bool:
        resp = self.request("/version")
        return resp.status_code == 200

    def get_nodes(self) -> list[str]:
        response = self.request("/nodes")

        data = response.json()
        nodes = [node["node"] for node in data.get("data", [])]

        return nodes

    def get_servers_brief(self) -> list[models.ServerBrief]:
        servers = []
        for node in self.get_nodes():
            res = self.request(f"/nodes/{node}/qemu")
            data = res.json()

            for server in data.get("data", []):
                servers.append(
                    models.ServerBrief(
                        server_id=server.get("vmid", 0),
                        name=server.get("name", ""),
                        status=models.ServerStatus(server.get("status", "stopped")),
                        cpus=server.get("cpus", 0),
                        cpu_usage=server.get("cpu", 0),
                        memory=server.get("maxmem", 0),
                        memory_used=server.get("mem", 0),
                        uptime=server.get("uptime", 0),
                    )
                )
        return servers
