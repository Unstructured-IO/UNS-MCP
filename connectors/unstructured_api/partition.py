import json
import os
from pathlib import Path
from typing import Literal

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


async def call_api(partition_params: PartitionParameters) -> list[dict]:
    partition_params.split_pdf_page = True
    partition_params.split_pdf_allow_failed = True
    partition_params.split_pdf_concurrency_level = 15

    request = PartitionRequest(partition_parameters=partition_params)

    res = await client.general.partition_async(request=request)
    return res.elements


async def partition_local_file(
    input_file_path: str,
    output_file_dir: str,
    strategy: Strategy = Strategy.VLM,
    vlm_model: VLMModel = VLMModel.CLAUDE_3_5_SONNET_20241022,
    vlm_model_provider: VLMModelProvider = VLMModelProvider.ANTHROPIC,
    output_type: Literal["json", "markdown"] = "json",
) -> str:
    """
    Transform a local file into structured data using the Unstructured API

    Args:
        input_file_path: The absolute path to the file
        output_file_dir: The absolute path to the directory where output file should be saved.
        strategy:
            Available strategies:
                VLM - most advanced transformation suitable for difficult PDFs and Images
                hi_res - high resolution transformation suitable for most document types
                fast - fast transformation suitable for PDFs with extractable text
                auto - automatically choose the best strategy based on the input file
        vlm_model: The VLM model to use for the transformation
        vlm_model_provider: The VLM model provider to use for the transformation
        output_type: The type of output to generate. Can be 'json' or 'markdown'.

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

    output_dir_path = Path(output_file_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    if output_type not in ["json", "markdown"]:
        return "Output type must be either 'json' or 'markdown'."
    elif output_type == "json":
        json_elements_as_str = json.dumps(response, indent=2)
        output_file = output_dir_path / Path(input_file_path).with_suffix(".json").name
        output_file.write_text(json_elements_as_str)
    else:
        markdown = f"# {Path(input_file_path).name}\n\n"

        for element in response:
            if element.get("type") == "Table":
                text_as_html = element.get("metadata", {}).get("text_as_html", "<></>")
                markdown += f"{text_as_html}\n\n"
            elif element.get("type") == "Header":
                text = element.get("text", "")
                markdown += f"## {text}\n\n"
            else:
                text = element.get("text", "")
                markdown += f"{text}\n\n"

        output_file = output_dir_path / Path(input_file_path).with_suffix(".md").name
        output_file.write_text(markdown)

    return f"Partition file {input_file_path} to {str(output_file)} successfully"
