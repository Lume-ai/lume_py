from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from lume_py.endpoints.config import get_settings
from lume_py.endpoints.workshop import WorkShop
from lume_py.endpoints.results import Result

settings = get_settings()

class Job(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    target_schema_id: Optional[str] = None
    source_schema_id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True

    @staticmethod
    async def get_jobs_data_page(page: int = 1, size: int = 50) -> List['Job']:
        response = await settings.client.fetch_paginated_data('jobs', page, size)
        return [Job(**item) for item in response['items']]

    @classmethod
    async def create(cls, pipeline_id: str, source_data: List[Dict[str, Any]]) -> 'Job':
        response = await settings.client.post(f'pipelines/{pipeline_id}/jobs', {'data': source_data})
        return cls(**response)

    @classmethod
    async def get_job_by_id(cls, job_id: str) -> 'Job':
        response = await settings.client.get(f'jobs/{job_id}')
        return cls(**response)

    async def delete(self) -> None:
        if not self.id:
            raise ValueError("Job ID is required for deletion.")
        await settings.client.delete(f'jobs/{self.id}')

    async def run(self, immediate: bool = False) -> Result:
        response = await settings.client.post(f'jobs/{self.id}/run')
        status = response['status']
        result_id = response['id']
        
        if immediate is True:
            return Result(**response)
        else:
            while status in ['queued', 'running']:
                result = await settings.client.get(f'results/{result_id}')
                status = result['status']
            return Result(**result)
    
    async def create_workshop(self):
        response = await settings.client.post(f'jobs/{self.id}/workshops')
        return WorkShop(**response)

    async def get_workshops(self, page: int = 1, size: int = 50) -> List[WorkShop]:
        response = await settings.client.fetch_paginated_data(f'jobs/{self.id}/workshops', page, size)
        return [WorkShop(**workshop) for workshop in response['items']]

    async def get_target_schema(self) -> Dict[str, Any]:
        return await settings.client.get(f'jobs/{self.id}/target_schema')

    @classmethod
    async def create_and_run(cls, pipeline_id: str, source_data: List[Dict[str, Any]]) -> Result:
        job = await cls.create(pipeline_id, source_data)
        return await job.run()

    async def get_results(self, page: int = 1, size: int = 50) -> List[Result]:
        response = await settings.client.fetch_paginated_data(f'jobs/{self.id}/results', page, size)
        return [Result(**result) for result in response['items']]
