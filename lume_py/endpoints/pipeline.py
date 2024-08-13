from typing import Optional, Dict, List, Any, Tuple
import httpx
from pydantic import BaseModel, Field
from lume_py.endpoints.config import get_settings
from lume_py.endpoints.jobs import Job
from lume_py.endpoints.workshop import WorkShop
from lume_py.endpoints.mappers import Mapper

settings = get_settings()


class PipelineCreatePayload(BaseModel):
    name: str = Field(..., example="Example Pipeline")
    description: str = Field(None, example="This is an example pipeline.")
    target_schema: Dict[str, Any] = Field(..., example={
        "type": "object",
        "properties": {
            "field": {"type": "string"}
        }
    })

    class Config:
        schema_extra = {
            "example": {
                "name": "Example Pipeline",
                "description": "This is an example pipeline.",
                "target_schema": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string"}
                    }
                }
            }
        }

        
        
class PipelineUpdatePayload(BaseModel):
    name: str
    description: str
    
    

class PipelineUploadSheets(BaseModel):
    file: Tuple[str, bytes, str]  
    pipeline_map_list: Optional[str] = Field(default=None, exclude=True) 
    second_table_row_to_insert: Optional[int] = Field(default=None, exclude=True)  

    class Config:
        schema_extra = {
            "example": {
                "file": ("example.xlsx", b"binarydata", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                "pipeline_map_list": "map1,map2,map3",
                "second_table_row_to_insert": 5
            }
        }

class PipelinePopulateSheets(BaseModel):
    pipeline_ids: str
    populate_excel_payload: str
    file_type: str

    class Config:
        orm_mode = True
        
        
class Pipeline(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    target_schema_id: Optional[str] = None
    source_schema_id: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None
    target_schema: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

    @staticmethod
    async def get_pipelines_data_page(page: int = 1, size: int = 50) -> List['Pipeline']:
        response = await settings.client.fetch_paginated_data('pipelines', page, size)
        return [Pipeline(**item) for item in response['items']]

    @classmethod
    async def create(cls, name: str, target_schema: Dict[str, Any], description: Optional[str] = None) -> 'Pipeline':
        payload = {
            "name": name,
            "target_schema": target_schema,
            "description": description
        }
        response = await settings.client.post('pipelines', payload)
        return cls(**response)

    @classmethod
    async def get_pipeline_by_id(cls, pipeline_id: str) -> 'Pipeline':
        response = await settings.client.get(f'pipelines/{pipeline_id}')
        return cls(**response)

    async def update(self, name: str, description: str) -> 'Pipeline':
        if not self.id:
            raise ValueError("Pipeline ID is required for updating.")
        payload = {'name': name, 'description': description}
        response = await settings.client.put(f'pipelines/{self.id}', payload)
        return Pipeline(**response)

    async def delete(self) -> None:
        if not self.id:
            raise ValueError("Pipeline ID is required for deletion.")
        await settings.client.delete(f'pipelines/{self.id}')

    async def create_job(self, source_data: List[Dict[str, Any]]) -> Job:
        if not self.id:
            raise ValueError("Pipeline ID is required for creating a job.")
        response = await settings.client.post(f'pipelines/{self.id}/jobs', {'data': source_data})
        return Job(**response)

    async def get_workshops(self, page: int = 1, size: int = 50) -> List[WorkShop]:
        if not self.id:
            raise ValueError("Pipeline ID is required for fetching workshops.")
        response = await settings.client.fetch_paginated_data(f'pipelines/{self.id}/workshops', page, size)
        return [WorkShop(**workshop) for workshop in response['items']]

    async def create_workshop(self) -> WorkShop:
        if not self.id:
            raise ValueError("Pipeline ID is required for creating a workshop.")
        response = await settings.client.post(f'pipelines/{self.id}/workshops')
        return WorkShop(**response)

    async def get_target_schema(self) -> Dict[str, Any]:
        if not self.id:
            raise ValueError("Pipeline ID is required for fetching target schema.")
        return await settings.client.get(f'pipelines/{self.id}/target_schema')

    async def get_mapper(self) -> Dict[str, Any]:
        if not self.id:
            raise ValueError("Pipeline ID is required for fetching mapper.")
        response = await settings.client.get(f'pipelines/{self.id}/mapper')
        if response is None:
            raise ValueError("No mapper found for this pipeline, consider running the job first.")
        return Mapper(**response)
    

    async def learn(self, target_property_names: Optional[List[str]] = None) -> None:
        if not self.id:
            raise ValueError("Pipeline ID is required for learning.")
        payload = {'target_field_names': target_property_names}
        await settings.client.post(f'pipelines/{self.id}/learn', payload)

    async def run_pipeline(self, source_data: List[Dict[str, Any]], immediate: bool = False) -> Mapper:
        if not self.id:
            raise ValueError("Pipeline ID is required for running the pipeline.")
        response = await settings.client.post(f'pipeline/{self.id}/run', {'data': source_data})
        status = response['status']
        result_id = response['id']
        if immediate is True:
            return Mapper(**response)
        else:
            while status in ['queued', 'running']:
                result = await settings.client.get(f'mappings/{result_id}')
                status = result['status']
            if result is None:
                raise ValueError("No mapper found for this pipeline, consider running the job first.")
            return Mapper(**result)

    async def upload_sheets(self, file_path: str, pipeline_map_list: Optional[str] = '', second_table_row_to_insert: Optional[int] = None):
        with open(file_path, 'rb') as file:
            files = {'file': (file_path, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {
                'pipeline_map_list': pipeline_map_list,
                'second_table_row_to_insert': second_table_row_to_insert
            }
            async with httpx.AsyncClient(timeout=60) as cli:
                response = await cli.post('https://api.lume.ai/crud/pipelines/upload/sheets', headers={'lume-api-key': settings.lume_api_key}, files=files, data=data)
                response.raise_for_status()
                return response.json()

    async def populate_sheets(self, pipeline_ids: str, populate_excel_payload: str, file_type: str) -> Dict[str, Any]:
        sheets_data = PipelinePopulateSheets(pipeline_ids=pipeline_ids, populate_excel_payload=populate_excel_payload, file_type=file_type)
        return await settings.client.post('pipelines/populate/sheets', sheets_data.model_dump())

    async def get_images(self) -> Dict[str, Any]:
        if not self.id:
            raise ValueError("Pipeline ID is required for fetching images.")
        return await settings.client.post(f'pipelines/{self.id}/populate/images')
