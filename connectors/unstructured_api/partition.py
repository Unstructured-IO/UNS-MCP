import json
import os
from pathlib import Path

import unstructured_client
from unstructured_client.models.operations import PartitionRequest
from unstructured_client.models.shared import (
    Files,
    PartitionParameters,
    Strategy,
    VLMModel,
    VLMModelProvider,
)

client = unstructured_client.UnstructuredClient(api_key_auth=os.getenv("UNSTRUCTURED_API_KEY"))


async def call_api(partition_params: PartitionParameters) -> str:
    partition_params.split_pdf_page = True
    partition_params.split_pdf_allow_failed = True
    partition_params.split_pdf_concurrency_level = 15

    request = PartitionRequest(partition_parameters=partition_params)

    res = await client.general.partition_async(request=request)
    json_elements = json.dumps(res.elements, indent=2)

    return json_elements


async def partition_local_file(
    input_file_path: str,
    strategy: Strategy = Strategy.VLM,
    vlm_model: VLMModel = VLMModel.CLAUDE_3_5_SONNET_20241022,
    vlm_model_provider: VLMModelProvider = VLMModelProvider.ANTHROPIC,
    output_file_path: str = "output",
) -> str:
    """
    Transform a local file into structured data using the Unstructured API

    Args:
        input_file_path: The absolute path to the file
        strategy:
            Available strategies:
                VLM - most advanced transformation suitable for difficult PDFs and Images
                hi_res - high resolution transformation suitable for most document types
                fast - fast transformation suitable for PDFs with extractable text
                auto - automatically choose the best strategy based on the input file
        vlm_model: The VLM model to use for the transformation
        vlm_model_provider: The VLM model provider to use for the transformation
        output_file_path: The absolute path to the output file

    Returns:
        A string containing the structured data or a message indicating the output
        file path with the structured data

    """
    try:
        with open(input_file_path, "rb") as content:
            partition_params = PartitionParameters(
                files=Files(
                    content=content,
                    file_name=os.path.basename(input_file_path),
                ),
                strategy=strategy,
                vlm_model=vlm_model,
                vlm_model_provider=vlm_model_provider,
            )
            response = await call_api(partition_params)
    except Exception as e:
        return str(e)

    Path.mkdir(Path(output_file_path).parent, parents=True, exist_ok=True)
    Path(output_file_path).write_text(response)
    return f"Partition file {input_file_path} to {output_file_path} successfully"
