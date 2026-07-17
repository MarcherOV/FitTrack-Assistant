import logging
from typing import Dict, Optional, Any
import httpx
from httpx import HTTPStatusError, RequestError, TimeoutException
import certifi

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str, secret_token: str, timeout: float = 5.0):
        self.base_url = base_url
        self.timeout = timeout

        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout,
                                         headers={
                                             "Content-Type": "application/json",
                                             "Accept": "application/json",
                                             "X-Bot-Secret": secret_token
                                         },
                                         verify=certifi.where())
        
    async def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None,
                       json_data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"/{endpoint.lstrip('/')}"
        try:
            response = await self._client.request(method=method, url=url, params=params, json=json_data)
            response.raise_for_status()
            
            if response.status_code == 204:
                return None
            
            return response.json()
        
        except HTTPStatusError as e:
            logger.error(
                f"API Mistake {e.response.status_code} [{method} {url}]"
            )
            raise e
        
        except TimeoutError:
            logger.error(
                f"API Timeout [{method} {url}]"
            )
            raise
        except RequestError as e:
            logger.error(
                f"Mistake with network [{method} {url}]"
            )
            raise

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,) -> Any:
        return await self._request("GET", endpoint, params)
    
    async def post(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                       json_data: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("POST", endpoint, params, json_data)
    
    async def patch(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                       json_data: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("PATCH", endpoint, params, json_data)
    
    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("DELETE", endpoint)
    
    async def close(self) -> None:
        await self._client.aclose()
        logger.info("API Client is closed")
