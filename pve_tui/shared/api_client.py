import urllib3
from requests import Session, Response
from urllib3.exceptions import SecurityWarning

# Most of Proxmox VE instances use self-signed certificates, so we disable warnings here.
urllib3.disable_warnings(SecurityWarning)


class APIClient:
    proxmox_base_url: str

    auth_token_id: str
    auth_token: str
    session: Session

    def __init__(self, proxmox_base_url: str, auth_token_id: str, auth_token: str) -> None:
        self.proxmox_base_url = proxmox_base_url
        self.auth_token_id = auth_token_id
        self.auth_token = auth_token

        self.session = Session()
        self.session.verify = False
        self.session.headers.update({
            "Authorization": f"PVEAPIToken={self.auth_token_id}={self.auth_token}"
        })


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
        resp = self.request('/version')
        return resp.status_code == 200
