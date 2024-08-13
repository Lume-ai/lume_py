import httpx
import lume_py as lume
import os
import pytest
import json


# Set the API key
api_key = os.environ.get('LUME_API_TOKEN')
if not api_key:
    raise EnvironmentError("LUME_API_TOKEN environment variable is not set.")

# Load target and source data from files
target_data_path = os.path.join(os.getcwd(), "tests/data/target.json")
source_data_path = os.path.join(os.getcwd(), "tests/data/source.json")

with open(target_data_path, encoding='utf-8') as f:
    target_data = json.load(f)

with open(source_data_path, encoding='utf-8') as f:
    source_data = json.load(f)

@pytest.mark.asyncio
async def test_pdf_workflow():
    lume.set_api_key(api_key)
    
    pdf_path = '...'
    
    try:
        extracted_pdf = await lume.PDF.extract_pdf(pdf_path=pdf_path)
        assert extracted_pdf is not None

        pdf_url = await lume.PDF.get_pdf_url(pdf_id=extracted_pdf['id'])
        assert pdf_url.startswith('https://')

    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        print(exc.response.json())
        raise

@pytest.mark.asyncio
async def test_result_workflow():
    lume.set_api_key(api_key)
    
    try:
        result = await lume.Result.get_results()
        assert result is not None

        spec = await result[0].get_spec()

        assert spec is not None

    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        print(exc.response.json())
        raise

@pytest.mark.asyncio
async def test_target_workflow():
    lume.set_api_key(api_key)
    
    try:
        target = await lume.Target.create(name='testing_target_sdk_4', filename='testing target sdk 3', target_schema=target_data)
        assert target is not None

        target_id = target.id
        fetched_target = await lume.Target.get_target_by_id(target_id)
        assert fetched_target is not None

        updated_target = await target.update(target_schema=target_data, name="updatedNew")
        
        assert updated_target is not None

    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        print(exc.response.json())
        raise

if __name__ == "__main__":
    pytest.main(["-v", __file__])
