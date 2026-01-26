from requests import Session, Request

class APIClient:
    proxmox_base_url: str
    user_name: str
    user_realm: str
    auth_token: str
    auth_token_name: str

    def __init__(self, proxmox_base_url: str, user_name: str, user_realm: str, auth_token: str, auth_token_name: str) -> None:
        self.proxmox_base_url = proxmox_base_url
        self.user_name = user_name
        self.user_realm = user_realm
        self.auth_token = auth_token
        self.auth_token_name = auth_token_name


    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"PVEAPIToken={self.user_name}@{self.user_realm}!{self.auth_token_name}={self.auth_token}"
        }

    @property
    def base_url(self) -> str:
        if not self.proxmox_base_url.endswith("/api2/json"):
            return f"{self.proxmox_base_url}/api2/json"
        return self.proxmox_base_url


    def create_request(self, url: str, method: str = "GET", **kwargs) -> Request:
        if not url.startswith("/"):
            url = f"/{url}"
        return Request(
            url=url,
            method=method,
            headers=self.headers,
            **kwargs
        )

    def is_healthy(self) -> bool:
        req = self.create_request('/version')
        with Session() as session:
            prepped = session.prepare_request(req)
            resp = session.send(prepped)
            return resp.status_code == 200
