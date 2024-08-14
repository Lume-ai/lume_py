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
    async def get_results(page: int = 1, size: int = 50, all: bool = False) -> List['Result']:
        """
        Fetches result data, either all results across pages or a single page of results.
        :param page: The page number to fetch (optional, defaults to 1).
        :param size: The number of items per page (optional, defaults to 50).
        :param all: Whether to fetch all pages of results (optional, defaults to False).
        :return: A list of results.
        """
        results = []
        if all:
            while True:
                response = await settings.client.fetch_paginated_data('results', page, size)
                results.extend([Result(**item) for item in response['items']])
                if not response['items'] or len(response['items']) < size:
                    break
                page += 1
        else:
            response = await settings.client.fetch_paginated_data('results', page, size)
            results.extend([Result(**item) for item in response['items']])
        return results
            

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

    async def get_mappings(self, all: bool = False) -> List[ResultMapper]:
        """
        Retrieves all mappings associated with a specific result, iterating through pages until all results are retrieved.
        :param all: Whether to fetch all pages of mappings (optional, defaults to False).
        :return: The list of mappings.
        """
        mappings = []
        page = 1
        size = 50
        if all:
            while True:
                response = await settings.client.fetch_paginated_data(f'results/{self.id}/mappings', page, size)
                mappings.extend([ResultMapper(**item) for item in response['items']])
                if not response['items'] or len(response['items']) < size:
                    break
                page += 1
        else:
            response = await settings.client.fetch_paginated_data(f'results/{self.id}/mappings', page, size)
            mappings.extend([ResultMapper(**item) for item in response['items']])
        return mappings

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

    
    async def get_failed(self):
        results = await self.get_results()
        res = []
        for result in results:
            if result.status == 'failed' or result.status == 'needs review':
                res.append(result)
        return res
    
        