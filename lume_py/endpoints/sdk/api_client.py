import httpx
from httpx import HTTPStatusError
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from http import HTTPMethod, HTTPStatus


class Pagination(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(50, ge=1)


class Lume:
    def __init__(self, api_key: str, base_url: str = "https://api.lume.ai/"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Content-Type": "application/json", "lume-api-key": self.api_key},
        )

    async def request(
        self,
        method: HTTPMethod,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        pagination: Optional[Pagination] = None,
    ) -> Dict[str, Any]:
        if pagination:
            params = params or {}
            params.update(pagination.model_dump())
        response = await self.client.request(method, url, params=params, json=json)
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            status_name = HTTPStatus(response.status_code).name
            raise HTTPStatusError(
                message=(
                    f"Error response {e.response.status_code} {status_name} for URL "
                    f"{e.response.url}: {e.response.text}"
                ),
                request=e.request,
                response=e.response,
            )
        return response.json()
