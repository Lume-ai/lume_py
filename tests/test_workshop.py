import lume_py as lume
import os
import pytest
import json
from httpx import HTTPStatusError

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
async def test_get_all():
    lume.set_api_key(api_key)

    try:
        paginated_results= await lume.WorkShop.get_workshops()
        assert isinstance(paginated_results, list)
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")


@pytest.mark.asyncio(scope="session")
async def test_workshop_get():
    lume.set_api_key(api_key)

    try:
        pipeline = await lume.Pipeline.get_pipeline_by_id("testingSDKPipeline2")
        workshop = await pipeline.create_workshop()
        getter = await lume.WorkShop.get_by_id(workshop.id)
        assert getter is not None
        
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")
        
        

if __name__ == "__main__":
    pytest.main(["-v", __file__])