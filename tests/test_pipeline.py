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
async def test_pipeline_create():
    lume.set_api_key(api_key)
    try:
        pipeline = await lume.Pipeline.create(name="testingSDKPipeline6", description="test", target_schema=target_data)
        assert pipeline is not None
        assert pipeline.name == "testingSDKPipeline6"
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")

@pytest.mark.asyncio(scope="session")
async def test_pipeline_get():
    lume.set_api_key(api_key)

    try:
        pipeline = await lume.Pipeline.get_pipeline_by_id("testingSDKPipeline2")
        print('error')
        assert pipeline.name == "testingSDKPipeline2"
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")

@pytest.mark.asyncio(scope="session")
async def test_pipeline_update():
    lume.set_api_key(api_key)

    try:
        pipeline_id = "testingSDKPipeline3"  # Use correct pipeline ID here
        pipeline = await lume.Pipeline.get_pipeline_by_id(pipeline_id)
        updated_pipeline = await pipeline.update(name="updated_pipeline_test_sdk_3", description="A test pipeline updated")
        assert updated_pipeline is not None
        assert updated_pipeline.name == "updated_pipeline_test_sdk_3"
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")

@pytest.mark.asyncio(scope="session")
async def test_pipeline_get_all():
    lume.set_api_key(api_key)

    try:
        paginated_pipelines = await lume.Pipeline.get_pipelines_data_page()
        assert isinstance(paginated_pipelines, list)
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")

@pytest.mark.asyncio
async def test_job_create():
    lume.set_api_key(api_key)

    try:
        pipeline = await lume.Pipeline.get_pipeline_by_id("testingSDKPipeline2")
        job = await lume.Job.create(pipeline_id=pipeline.id, source_data=source_data)
        result = await job.run()
        assert result.status == 'finished'
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")

@pytest.mark.asyncio
async def test_pipeline_mapper():
    lume.set_api_key(api_key)

    try:
        pipeline = await lume.Pipeline.create(
            name="emptyMapperPipelineTesting",
            description="test",
            target_schema=target_data
        )


        # Run job and check mapper
        await pipeline.run_job(source_data=source_data)
        mapper = await pipeline.get_mapper()
        assert mapper is not None, "Pipeline should have a mapper after running a job."
    except HTTPStatusError as e:
        pytest.fail(f"HTTP error occurred: {e}")


if __name__ == "__main__":
    pytest.main(["-v", __file__])