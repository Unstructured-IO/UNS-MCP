import json
import os
from pathlib import Path
from typing import Any, Literal

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
    output_type: Literal["json", "md"] = "json",
) -> str:
    """
    Transform a local file into structured data using the Unstructured API.

    Args:
        input_file_path: The absolute path to the file.
        output_file_dir: The absolute path to the directory where the output file should be saved.
        strategy: The strategy for transformation.
            Available strategies:
                VLM - most advanced transformation suitable for difficult PDFs and Images
                hi_res - high resolution transformation suitable for most document types
                fast - fast transformation suitable for PDFs with extractable text
                auto - automatically choose the best strategy based on the input file
        vlm_model: The VLM model to use for the transformation.
        vlm_model_provider: The VLM model provider to use for the transformation.
        output_type: The type of output to generate. Options: 'json' for json
                     or 'md' for markdown.

    Returns:
        A string containing the structured data or a message indicating the output file
        path with the structured data.
    """

    input_path = Path(input_file_path)
    output_dir_path = Path(output_file_dir)

    if output_type not in ["json", "md"]:
        return f"Invalid output type '{output_type}'. Must be 'json' or 'md'."

    try:
        with input_path.open("rb") as content:
            partition_params = PartitionParameters(
                files=Files(
                    content=content,
                    file_name=input_path.name,
                ),
                strategy=strategy,
                vlm_model=vlm_model,
                vlm_model_provider=vlm_model_provider,
            )
            response = await call_api(partition_params)
    except Exception as e:
        return f"Failed to partition file: {e}"

    output_dir_path.mkdir(parents=True, exist_ok=True)

    output_file = output_dir_path / input_path.with_suffix(f".{output_type}").name

    if output_type == "json":
        json_elements_as_str = json.dumps(response, indent=2)
        output_file.write_text(json_elements_as_str, encoding="utf-8")
    else:
        markdown = construct_markdown(response, input_path.name)
        output_file.write_text(markdown, encoding="utf-8")

    return f"Partitioned file {input_file_path} to {output_file} successfully."


def construct_markdown(elements_list: list[dict[str, Any]], file_name: str) -> str:
    """
    Constructs a markdown representation from the response data.

    Args:
        elements_list: The response data from the API call as a list of elements.
        file_name: The name of the input file.

    Returns:
        A markdown string.
    """
    markdown = f"# {file_name}\n\n"

    for element in elements_list:
        element_type = element.get("type", "")
        text = element.get("text", "")

        if element_type == "Table":
            text_as_html = element.get("metadata", {}).get("text_as_html", "<></>")
            markdown += f"{text_as_html}\n\n"
        elif element_type == "Header":
            markdown += f"## {text}\n\n"
        else:
            markdown += f"{text}\n\n"

    return markdown
