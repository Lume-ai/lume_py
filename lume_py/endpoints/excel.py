import httpx
from typing import Dict, Any
from lume_py.endpoints.config import get_settings

settings = get_settings()

class Excel:
    """
    Service class for convenience methods related to Excel operations.
    """

    @staticmethod
    async def convert_sheets(file_path: str, name: str, sheets: str = '') -> Dict[str, Any]:
        """
        Convert an Excel file to structured JSON data

        :param file_path: The path to the Excel file to upload.
        :param name: The name of the file including the extension.
        :param sheets: The names of the sheets in the file you want to include in the conversion given in comma delimited format. If not provided, all sheets will be included.
        :return: A dictionary containing the response data.
        :raises Exception: If the file cannot be uploaded or other errors occur.
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                data = {'name': name, 'sheets': sheets}
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        'https://staging.lume-terminus.com/crud/convert/sheets',
                        files=files,
                        data=data,
                        headers={'accept': 'application/json', 'lume-api-key': settings.client.api_key}
                    )
                    response.raise_for_status()
                    return response.json()
        except Exception as exc:
            raise exc

    @staticmethod
    async def get_pivot_tasks(page: int = 1, size: int = 50) -> Dict[str, Any]:
        """
        Retrieves a list of all Excel pivot tasks.
        
        :param page: Page number to retrieve.
        :param size: Number of items per page.
        :return: A dictionary containing the list of pivot tasks.
        :raises Exception: If the request fails or other errors occur.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://staging.lume-terminus.com/crud/excel/pivot',
                    params={'page': page, 'size': size},
                    headers={'lume-api-key': settings.client.api_key}
                )
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            raise exc

    @staticmethod
    async def get_pivot_task_status(task_id: str) -> Dict[str, Any]:
        """
        Retrieves the status of a specific Excel pivot task.
        
        :param task_id: The ID of the pivot task.
        :return: A dictionary containing the task status.
        :raises Exception: If the request fails or other errors occur.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'https://staging.lume-terminus.com/crud/excel/pivot/{task_id}',
                    headers={'lume-api-key': settings.client.api_key}
                )
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            raise exc

    @staticmethod
    async def get_pivot_task_url(task_id: str) -> Dict[str, Any]:
        """
        Retrieves the URL of a specific Excel pivot task file.
        
        :param task_id: The ID of the pivot task.
        :return: A dictionary containing the URL of the Excel file.
        :raises Exception: If the request fails or other errors occur.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'https://staging.lume-terminus.com/crud/excel/pivot/{task_id}/url',
                    headers={'lume-api-key': settings.client.api_key}
                )
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            raise exc
