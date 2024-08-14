from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from lume_py.endpoints.config import get_settings

settings = get_settings()

class Target(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    name: Optional[str] = None
    filename: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

    @staticmethod
    async def get(page: int = 1, size: int = 50, all: bool = False) -> List['Target']:
        """
        Retrieves all target schemas, iterating through pages until all schemas are retrieved.
        :param page: The page number to fetch (optional, defaults to 1).
        :param size: The number of items per page (optional, defaults to 50).
        :param all: Whether to fetch all pages of target schemas (optional, defaults to False).
        :return: A list of target schemas.
        """
        targets = []
        if all:
            while True:
                response = await settings.client.fetch_paginated_data('target_schemas', page, size)
                targets.extend([Target(**item) for item in response['items']])
                if not response['items'] or len(response['items']) < size:
                    break
                page += 1
        else:
            response = await settings.client.fetch_paginated_data('target_schemas', page, size)
            targets.extend([Target(**item) for item in response['items']])
        
        return targets

    @staticmethod
    async def create(target_schema: Dict[str, Any], name: str = "string",  filename: str = "string") -> 'Target':
        """
        Creates a new target schema.
        :param target_schema: The schema to create.
        :param name: The name of the schema.
        :param description: The description of the schema.
        :param filename: The filename of the schema.
        :return: The created target schema.
        """
        payload = {
            'name': name,
            'schema': target_schema,
            'filename': filename
        }
        response = await settings.client.post('target_schemas', payload)
        return Target(**response)

    @classmethod
    async def get_schema_by_id(cls, target_schema_id: str) -> Dict[str, Any]:
        """
        Retrieves a target schema by its ID.
        :param target_schema_id: The ID of the target schema to retrieve.
        :return: The target schema details.
        """
        response = await settings.client.get(f'target_schemas/{target_schema_id}')
        return response

    @staticmethod
    async def get_target_by_id(target_id, page: int = 1, size: int = 50) -> List['Target']:
        """
        Retrieves all target schemas.
        :return: List of target schemas.
        """
        response = await Target.get(page, size)
        for target in response:
            if target.id == target_id:
                return target
    
    async def get_schema(self) -> Dict[str, Any]:
        """
        Retrieves the details of this target schema.
        :return: The target schema details.
        """
        response = await settings.client.get(f'target_schemas/{self.id}')
        return response

    async def delete(self) -> None:
        """
        Deletes a specific target schema by its ID.
        """
        await settings.client.delete(f'target_schemas/{self.id}')

    async def update(self, name: str = "string", filename: str = "string", target_schema: Dict[str, Any] = {}) -> 'Target':
        """
        Updates an existing target schema with the provided details.
        :param name: The new name of the schema.
        :param description: The new description of the schema.
        :param filename: The new filename of the schema.
        :param target_schema: The new target schema.
        :return: The updated target schema details.
        """
        payload = {
            'name': name,
            'filename': filename,
            'schema': target_schema
        }
        response = await settings.client.put(f'target_schemas/{self.id}/update', data=payload)
        return response

    async def get_target_schema_object(self) -> 'Target':
        """
        Retrieves the object of a specific target schema by its ID.
        :return: The target schema object.
        """
        response = await settings.client.get(f'target_schemas/{self.id}/object')
        return Target(**response)

    @staticmethod
    async def generate_target_schema(sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a new target schema.
        :param sample: The sample data to generate the schema.
        :return: The generated target schema details.
        """
        response = await settings.client.post('target_schemas/generate', {'sample': sample})
        return response
