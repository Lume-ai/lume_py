from typing import List, Dict, Any, Optional
from lume_py.endpoints.config import get_settings
from lume_py.endpoints.results import Result
from lume_py.endpoints.mappers import Mapping
from .sdk.api_client import Pagination
from http import HTTPMethod

from pydantic import BaseModel

settings = get_settings()

class WorkShop(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    job_id: Optional[str] = None
    target_schema_id: Optional[str] = None
    source_schema_id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True
    @staticmethod
    async def get_workshops(page: int = 1, size: int = 50, all: bool = False) -> List['WorkShop']:
        """
        Fetches all workshop data, iterating through pages until all workshops are retrieved.
        :param page: The page number to fetch (optional, defaults to 1).
        :param size: The number of items per page (optional, defaults to 50).
        :param all: Whether to fetch all pages of workshops (optional, defaults to False).
        :return: A list of workshops.
        """
        workshops = []
        pagination = Pagination(page=page, size=size)
        if all:
            while True:
                response = await settings.client.request(
                    method=HTTPMethod.GET, url="workshops", pagination=pagination
                )
                workshops.extend([WorkShop(**item) for item in response["items"]])
                if not response["items"] or len(response["items"]) < size:
                    break
                page += 1
        else:
            response = await settings.client.request(
                method=HTTPMethod.GET, url="workshops", pagination=pagination
            )
            workshops.extend([WorkShop(**item) for item in response["items"]])

        return workshops

    @classmethod
    async def get_by_id(cls, workshop_id: str) -> 'WorkShop':
        """
        Retrieves details of a specific workshop.
        :param workshop_id: The ID of the workshop to fetch details for.
        :return: Workshop details.
        """
        response = await settings.client.request(
            method=HTTPMethod.GET, url=f"workshops/{workshop_id}"
        )
        return cls(**response)

    async def get_details(self) -> 'WorkShop':
        """
        Retrieves the details of this workshop.
        :return: The workshop details.
        """
        response = await settings.client.request(
            method=HTTPMethod.GET, url=f"workshops/{self.id}"
        )
        return WorkShop(**response)

    async def delete(self) -> Dict[str, Any]:
        """
        Deletes a workshop with the specified ID.
        :return: Success message on successful deletion.
        """
        return await settings.client.request(
            method=HTTPMethod.DELETE, url=f"workshops/{self.id}"
        )

    async def run_mapper(self, mapper: List[Dict[str, Any]], immediate: bool = False) -> Dict[str, Any]:
        """
        Runs the mapper of a workshop with the specified ID.
        :param mapper: Details required for running the mapper.
        :return: The result of running the mapper.
        """
        response = await settings.client.request(
            method=HTTPMethod.POST,
            url=f"workshops/{self.id}/mapper/run",
            json={"mapper": mapper},
        )
        response_status = response["status"]

        if immediate:
            return Result(**response)
        else:
            while response_status in ["queued", "running"]:
                response = await settings.client.request(
                    method=HTTPMethod.GET, url=f'results/{response["id"]}'
                )
                response_status = response["status"]
            return Result(**response)
        
    async def update_representative_sample(self, target_field_name: str, mapper: Dict[str, Any]) -> 'Mapping':
        """
        Runs the mapper of a workshop with the specified ID.
        :param mapper: Details required for running the mapper.
        :return: The result of running the mapper.
        """

        if not self.pipeline_id:
            raise ValueError("Pipeline ID is required for fetching mapper.")
        response = await settings.client.request(
            method=HTTPMethod.GET, url=f"pipelines/{self.pipeline_id}/mapper"
        )
        if response is None:
            raise ValueError("No mapper found for this pipeline, consider running the job first.")
        
        updated_mapper = None
        for val in response:
            if val['targetField'] == target_field_name:
                updated_mapper = val
                if 'transformation' in val and 'params' in val['transformation'] and 'lookup' in val['transformation']['params']:
                    updated_mapper['transformation']['params']['lookup'] = mapper
        if not updated_mapper:
            raise ValueError(f"Could not find {target_field_name} within the mapper")
        
        response = await settings.client.request(
            method=HTTPMethod.POST,
            url=f"workshops/{self.id}/mapper/run",
            json={"mapper": [updated_mapper]},
        )
        return Mapping(**response)

    async def run_sample(self, sample: Dict[str, Any], immediate: bool = False) -> Dict[str, Any]:
        """
        Runs a sample for the workshop with the specified ID.
        :param sample: Details required for running the sample.
        :return: The result of running the sample.
        """
        response = await settings.client.request(
            method=HTTPMethod.POST,
            url=f"workshops/{self.id}/sample/run",
            json={"sample": sample},
        )
        response_status = response["status"]

        if immediate:
            return Result(**response)
        else:
            while response_status in ["queued", "running"]:
                response = await settings.client.request(
                    method=HTTPMethod.GET, url=f'results/{response["id"]}'
                )
                response_status = response["status"]
            return Result(**response)

    async def run_target_schema(self, target_schema: Dict[str, Any], immediate: bool = False) -> Dict[str, Any]:
        """
        Runs the target schema for the workshop with the specified ID.
        :param target_schema: Details required for running the target schema.
        :return: The result of running the target schema.
        """
        # implement polling
        response = await settings.client.request(
            method=HTTPMethod.POST,
            url=f"workshops/{self.id}/target_schema/run",
            json={"target_schema": target_schema},
        )
        response_status = response["status"]

        if immediate:
            return Result(**response)
        else:
            while response_status in ["queued", "running"]:
                response = await settings.client.request(
                    method=HTTPMethod.GET, url=f'results/{response["id"]}'
                )
                response_status = response["status"]

            return Result(**response)

    async def run_prompt(self, target_fields_to_prompt: Dict[str, Any], immediate: bool = False) -> Dict[str, Any]:
        """
        Runs the prompts for the workshop with the specified ID.
        :param target_fields_to_prompt: Details required for running the prompt.
        :return: The result of running the prompt.
        """
        response = await settings.client.request(
            method=HTTPMethod.POST,
            url=f"workshops/{self.id}/prompt/run",
            json={"target_fields_to_prompt": target_fields_to_prompt},
        )
        response_status = response["status"]

        if immediate:
            return Result(**response)
        else:
            while response_status in ["queued", "running"]:
                response = await settings.client.request(
                    method=HTTPMethod.GET, url=f'results/{response["id"]}'
                )
                response_status = response["status"]

            return Result(**response)

    async def deploy(self) -> Dict[str, Any]:
        """
        Deploys the workshop with the specified ID.
        :return: The deployed workshop details.
        """
        response = await settings.client.request(
            method=HTTPMethod.POST, url=f"workshops/{self.id}/deploy"
        )
        return WorkShop(**response)

    async def get_results(self, page: int = 1, size: int = 50, all: bool = False) -> List[Result]:
        """
        Retrieves results associated with a specific workshop, iterating through pages until all results are retrieved.
        :param page: The page number to fetch (optional, defaults to 1).
        :param size: The number of items per page (optional, defaults to 50).
        :param all: Whether to fetch all pages of results (optional, defaults to False).
        :return: A list of results.
        """
        results = []
        pagination = Pagination(page=page, size=size)
        if all:
            while True:
                response = await settings.client.request(
                    method=HTTPMethod.GET,
                    url=f"workshops/{self.id}/results",
                    pagination=pagination,
                )
                results.extend([Result(**item) for item in response["items"]])
                if not response["items"] or len(response["items"]) < size:
                    break
                page += 1
        else:
            response = await settings.client.request(
                method=HTTPMethod.GET,
                url=f"workshops/{self.id}/results",
                pagination=pagination,
            )
            results.extend([Result(**item) for item in response["items"]])

        return results

    async def get_target_schema(self) -> Dict[str, Any]:
        """
        Retrieves the target schema for a specific workshop.
        :return: The target schema for the workshop.
        """
        return await settings.client.request(
            method=HTTPMethod.GET, url=f"workshops/{self.id}/target_schema"
        )

    async def get_mapping(self) -> List[Dict[str, Any]]:
        """
        Retreives the mappings transformations associated with the workshop.
        Returns:
            List[Dict[str, Any]]: The mapping
        """
        return await settings.client.request(
            method=HTTPMethod.GET, url=f"workshops/{self.id}/mapper"
        )
