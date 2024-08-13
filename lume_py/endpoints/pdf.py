import httpx
from lume_py.endpoints.config import get_settings

settings = get_settings()

class PDF:
    """
    Service class for PDF-related workflows.
    This may include custom endpoints for specific use cases.
    """


    @staticmethod
    async def process_adv_form(pdf_path: str):
        """
        Processes an advanced form PDF.
        :param pdf_path: The path to the PDF file to process.
        :return: A dictionary representing the processed PDF result.
        """
        
        async with httpx.AsyncClient() as client:
            with open(pdf_path, 'rb') as pdf_file:
                files = {'file': (pdf_path, pdf_file, 'application/pdf')}
                response = await client.post(
                    'https://staging.lume-terminus.com/crud/pdf/adv',
                    files=files,
                    headers={'lume-api-key': settings.client.api_key}
                )
                response.raise_for_status()
                response = response.json()
                status = response['status']
                
                while status in ['QUEUED', 'PENDING']:
                    response = await client.get(f'https://staging.lume-terminus.com/crud/pdf/adv/{response["id"]}', headers={'lume-api-key': settings.client.api_key})
                    response = response.json()
                    status = response['status']
                return response

    @staticmethod
    async def get_adv_form(pdf_id):
        """
        Retrieves an advanced form PDF by its ID.
        :return: FileResult object representing the PDF.
        """
        return await settings.client.get(f'pdf/adv/{pdf_id}')

    @staticmethod
    async def get_adv_forms_page(page: int = 1, size: int = 50):
        """
        Retrieves a paginated list of advanced form PDFs.
        :param page: The page number (optional, defaults to 1).
        :param size: The number of items per page (optional, defaults to 50).
        :return: PaginatedResponse containing FileResult objects.
        """
        return await settings.client.fetch_paginated_data('pdf/adv', page, size)

    @staticmethod
    async def get_adv_url(pdf_id: int):
        """
        Retrieves the URL of an advanced form PDF by its ID.
        :param pdf_id: The ID of the PDF form.
        :return: URL of the PDF.
        """
        try:
            body = await settings.client.get(f'pdf/adv/{pdf_id}/url')
            return body['url']
        except Exception as exc:
            raise exc

    @staticmethod
    async def extract_pdf(pdf_path: str, immediate: bool = False):
        """
        Extracts data from a PDF file.
        :param pdf_path: The path to the PDF file to process.
        :return: A dictionary representing the extracted PDF result.
        """
        async with httpx.AsyncClient() as client:
            with open(pdf_path, 'rb') as pdf_file:
                files = {'file': (pdf_path, pdf_file, 'application/pdf')}
                response = await client.post(
                    'https://staging.lume-terminus.com/crud/pdf/orders',
                    files=files,
                    headers={'lume-api-key': settings.client.api_key}
                )
                response.raise_for_status()
                response = response.json()
                status = response['status']
                if immediate is True:
                    return response
                else:
                    while status in ['QUEUED', 'PENDING']:
                        response = await client.get(f'https://staging.lume-terminus.com/crud/pdf/orders/{response["id"]}', headers={'lume-api-key': settings.client.api_key})
                        response = response.json()
                        status = response['status']
                    return response

    @staticmethod
    async def get_pdfs(page: int = 1, size: int = 50):
        """
        Retrieves a paginated list of PDF orders.
        :param page: The page number (optional, defaults to 1).
        :param size: The number of items per page (optional, defaults to 50).
        :return: PaginatedResponse containing FileResult objects.
        """
        return await settings.client.fetch_paginated_data('pdf/orders', page, size)

    @staticmethod
    async def get_pdf(pdf_id: int):
        """
        Retrieves a PDF order by its ID.
        :param pdf_id: The ID of the PDF order.
        :return: FileResult object representing the PDF.
        """
        return await settings.client.get(f'pdf/orders/{pdf_id}')

    @staticmethod
    async def get_pdf_url(pdf_id: int):
        """
        Retrieves the URL of a PDF order by its ID.
        :param pdf_id: The ID of the PDF order.
        :return: URL of the PDF.
        """
        try:
            body = await settings.client.get(f'pdf/orders/{pdf_id}/url')
            return body['url']
        except Exception as exc:
            raise exc
