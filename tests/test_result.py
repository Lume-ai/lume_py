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


@pytest.mark.asyncio(scope="session")
async def test_result():
    lume.set_api_key(api_key)

    try:
        pipe = await lume.Pipeline.create(name="testingSDKPipelineResults", description="test", target_schema=target_data)
        result = await lume.Job.create_and_run(pipeline_id=pipe.id, source_data=source_data)
        
        assert result.id != None
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")

@pytest.mark.asyncio(scope="session")
async def test_confidence_score():
    lume.set_api_key(api_key)

    try:
        results = await lume.Result.get_results()
        result = results[0]
        confidence = result.generate_confidence_scores()
        
        assert confidence != None
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")

@pytest.mark.asyncio(scope="session")
async def test_result_get_all():
    lume.set_api_key(api_key)

    try:
        paginated_results= await lume.Result.get_results()
        assert isinstance(paginated_results, list)
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")

@pytest.mark.asyncio
async def test_spec_change():
    lume.set_api_key(api_key)

    try:
        pipeline = await lume.Pipeline.get_pipeline_by_id("testingSDKPipeline2")
        job = await lume.Job.create(pipeline_id=pipeline.id, source_data=source_data)
        result = await job.run()
        first_spec = result.get_spec()
        
        # Change the spec
        workshop = await job.create_workshop()
        secondResult = await workshop.run_prompt({'product.weight': 'integer'})
        secondSpec = secondResult.get_spec()
        
        
        # check those fields to see the difference
        
        assert first_spec != secondSpec
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")




if __name__ == "__main__":
    pytest.main(["-v", __file__])