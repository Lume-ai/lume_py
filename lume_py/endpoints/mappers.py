from typing import Any, Optional, List, Dict
from pydantic import BaseModel
from lume_py.endpoints.config import get_settings
from http import HTTPMethod

settings = get_settings()

class Mapping(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    job_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    mapped_data: Optional[List[Dict[str, Any]]] = None

    class Config:
        orm_mode = True

    @staticmethod
    async def create(data: List[Dict[str, Any]], name: str, description: str, target_schema: Dict[str, Any]) -> 'Mapping':
        """
        Creates a new mapping.
        :param data: The data to map.
        :param name: The name of the mapping.
        :param description: The description of the mapping.
        :param target_schema: The target schema for the mapping.
        :return: The created mapping.
        """
        payload = {
            "data": data,
            "name": name,
            "description": description,
            "target_schema": target_schema,
        }
        response = await settings.client.request(
            method=HTTPMethod.POST, url="mapping", json=payload
        )
        return Mapping(**response)
    
    async def get_representative_sample(self, target_field_name: str) -> Dict[str, Any]:
        """
        Retrieves a Lookup dictionary.
        :param target_field_name: The name of the target field.
        """

        if not self.pipeline_id:
            raise ValueError("Pipeline ID is required for fetching mapper.")
        response = await settings.client.request(
            method=HTTPMethod.GET, url=f"pipelines/{self.pipeline_id}/mapper"
        )
        if response is None:
            raise ValueError("No mapper found for this pipeline, consider running the job first.")
        
        for mapper in response:
            if mapper['targetField'] == target_field_name:
                return mapper.get('transformation', {}).get('params', {}).get('lookup', {})
            
        raise ValueError(f"Could not find {target_field_name} within the mapper")

    @classmethod
    async def get_by_id(cls, result_id: str) -> 'Mapping':
        """
        Retrieves a mapping by its result ID.
        :param result_id: The ID of the result to retrieve the mapping for.
        :return: The mapping details.
        """
        response = await settings.client.request(
            method=HTTPMethod.GET, url=f"mappings/{result_id}"
        )
        return cls(**response)

    async def get_details(self) -> 'Mapping':
        """
        Retrieves the details of this mapping.
        :return: The mapping details.
        """
        response = await settings.client.request(
            method=HTTPMethod.GET, url=f"mappings/{self.id}"
        )
        return Mapping(**response)
