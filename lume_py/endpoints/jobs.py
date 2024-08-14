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
    async def get_all_jobs(page: int = 1, size: int = 50, all: bool = False) -> List['Job']:
        """
        Retrieves a paginated list of jobs or all jobs if 'all' is set to True.
        
        :param page: The page number to fetch (optional, defaults to 1).
        :param size: The number of items per page (optional, defaults to 50).
        :param all: If True, fetches all jobs by iterating through all pages (optional, defaults to False).
        :return: A list of Job objects.
        """
        jobs = []
        if all:
            while True:
                response = await settings.client.fetch_paginated_data('jobs', page, size)
                jobs.extend([Job(**item) for item in response['items']])
                if not response['items'] or len(response['items']) < size:
                    break
                page += 1
        else:
            response = await settings.client.fetch_paginated_data('jobs', page, size)
            jobs.extend([Job(**item) for item in response['items']])
        
        return jobs


    @classmethod
    async def create(cls, pipeline_id: str, source_data: List[Dict[str, Any]]) -> 'Job':
        """
        Creates a new job for a given pipeline.
        :param pipeline_id: The ID of the pipeline.
        :param source_data: The source data for the job.
        :return: The created Job object.
        """
        response = await settings.client.post(f'pipelines/{pipeline_id}/jobs', {'data': source_data})
        return cls(**response)

    @classmethod
    async def get_job_by_id(cls, job_id: str) -> 'Job':
        """
        Retrieves a job by its ID.
        :param job_id: The ID of the job.
        :return: The Job object.
        """
        response = await settings.client.get(f'jobs/{job_id}')
        return cls(**response)

    async def delete(self) -> None:
        """
        Deletes the current job.
        :raises ValueError: If the job ID is not set.
        """
        if not self.id:
            raise ValueError("Job ID is required for deletion.")
        await settings.client.delete(f'jobs/{self.id}')

    async def run(self, immediate: bool = False) -> Result:
        """
        Runs the job and returns the result.
        :param immediate: Whether to return the result immediately or wait until the job is complete.
        :return: The Result object.
        """
        response = await settings.client.post(f'jobs/{self.id}/run')
        status = response['status']
        result_id = response['id']
        
        if immediate:
            return Result(**response)
        else:
            while status in ['queued', 'running']:
                result = await settings.client.get(f'results/{result_id}')
                status = result['status']
            return Result(**result)
    
    async def create_workshop(self) -> WorkShop:
        """
        Creates a workshop for the current job.
        :return: The created WorkShop object.
        """
        response = await settings.client.post(f'jobs/{self.id}/workshops')
        return WorkShop(**response)

    async def get_workshops(self, page: int = 1, size: int = 50, all: bool = False) -> List[WorkShop]:
        """
        Retrieves workshops associated with the current job, optionally fetching all pages.
        :param page: The page number to fetch (optional, defaults to 1).
        :param size: The number of items per page (optional, defaults to 50).
        :param all: Whether to fetch all pages (optional, defaults to False).
        :return: A list of WorkShop objects.
        """
        workshops = []
        if all:
            while True:
                response = await settings.client.fetch_paginated_data(f'jobs/{self.id}/workshops', page, size)
                workshops.extend([WorkShop(**item) for item in response['items']])
                if not response['items'] or len(response['items']) < size:
                    break
                page += 1
        else:
            response = await settings.client.fetch_paginated_data(f'jobs/{self.id}/workshops', page, size)
            workshops.extend([WorkShop(**item) for item in response['items']])
        return workshops

    async def get_target_schema(self) -> Dict[str, Any]:
        """
        Retrieves the target schema associated with the current job.
        :return: A dictionary representing the target schema.
        """
        return await settings.client.get(f'jobs/{self.id}/target_schema')

    @classmethod
    async def create_and_run(cls, pipeline_id: str, source_data: List[Dict[str, Any]]) -> Result:
        """
        Creates and runs a job for a given pipeline.
        :param pipeline_id: The ID of the pipeline.
        :param source_data: The source data for the job.
        :return: The Result object from running the job.
        """
        job = await cls.create(pipeline_id, source_data)
        return await job.run()

    async def get_results(self, page: int = 1, size: int = 50, all: bool = False) -> List[Result]:
        """
        Retrieves results associated with the current job, optionally fetching all pages.
        :param page: The page number to fetch (optional, defaults to 1).
        :param size: The number of items per page (optional, defaults to 50).
        :param all: Whether to fetch all pages (optional, defaults to False).
        :return: A list of Result objects.
        """
        results = []
        if all:
            while True:
                response = await settings.client.fetch_paginated_data(f'jobs/{self.id}/results', page, size)
                results.extend([Result(**item) for item in response['items']])
                if not response['items'] or len(response['items']) < size:
                    break
                page += 1
        else:
            response = await settings.client.fetch_paginated_data(f'jobs/{self.id}/results', page, size)
            results.extend([Result(**item) for item in response['items']])
        return results
