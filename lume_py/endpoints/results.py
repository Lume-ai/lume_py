from typing import Any, Optional, List, Dict
from pydantic import BaseModel
from lume_py.endpoints.config import get_settings
import asyncio


settings = get_settings()

class ResultMapper(BaseModel):
    result_id: Optional[str] = None
    index: Optional[int] = None
    source_record: Optional[Dict] = None
    mapped_record: Optional[Dict] = None
    messsage: Optional[str] = None

    class Config:
        orm_mode = True

class Result(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True

    @staticmethod
    async def get_results(page: int = 1, size: int = 50) -> List['Result']:
        """
        Fetches all result data.
        """
        response = await settings.client.fetch_paginated_data('results', page, size)
        return [Result(**item) for item in response['items']]

    @classmethod
    async def get_by_id(cls, result_id: str) -> 'Result':
        """
        Retrieves a result by its ID.
        :param result_id: The ID of the result to retrieve.
        :return: The result details.
        """
        response = await settings.client.get(f'results/{result_id}')
        return cls(**response)

    async def get_details(self) -> 'Result':
        """
        Retrieves the details of this result.
        :return: The result details.
        """
        response = await settings.client.get(f'results/{self.id}')
        return Result(**response)

    async def get_spec(self) -> Dict[str, Any]:
        """
        Retrieves specifications associated with a specific result.
        :return: The specifications.
        """
        spec = await settings.client.get(f'results/{self.id}/spec')
        if spec:
            return spec
        else:
            raise ValueError("No spec found for this result, consider running the job first.")

    async def get_mappings(self) -> List[ResultMapper]:
        """
        Retrieves mappings associated with a specific result.
        :return: The list of mappings.
        """
        response = await settings.client.fetch_paginated_data(f'results/{self.id}/mappings')
        return [ResultMapper(**item) for item in response['items']]

    async def generate_confidence_scores(self, timeout: int = 10):
        """
        Generates confidence scores for a specific result.
        :param timeout: The timeout for the operation.
        :return: The confidence scores.
        """

        async def fetch_confidence_scores():
            confidence = await settings.client.post(f'results/{self.id}/confidence')
            status = confidence['status']
            while status in ['pending', 'running', 'queued']:
                confidence = await settings.client.get(f'results/{self.id}/confidence')
                status = confidence['status']
            return confidence

        try:
            confidence = await asyncio.wait_for(fetch_confidence_scores(), timeout)
        except Exception as exc:
            raise TimeoutError(f"Operation timed out after {timeout} seconds") from exc

        return confidence
