import httpx
from typing import Any, Dict, Optional

class Lume:
    def __init__(self, api_key: str, base_url: str = 'https://staging.lume-terminus.com/crud/'):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                'Content-Type': 'application/json',
                'lume-api-key': self.api_key
            }
        )

    async def fetch_paginated_data(self, endpoint: str, page: int = 1, size: int = 50) -> Dict[str, Any]:
        response = await self.client.get(endpoint, params={'page': page, 'size': size})
        response.raise_for_status()
        return response.json()

    async def fetch_paginated_data_with_params(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    async def post_paginated_data_with_params(self, endpoint: str, body: Dict[str, Any], page: int = 1, size: int = 50) -> Dict[str, Any]:
        response = await self.client.post(endpoint, json=body, params={'page': page, 'size': size})
        response.raise_for_status()
        return response.json()

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = await self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    async def put(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = await self.client.put(url, json=data)
        response.raise_for_status()
        return response.json()

    async def delete(self, url: str) -> Dict[str, Any]:
        response = await self.client.delete(url)
        response.raise_for_status()
        return response.json()
