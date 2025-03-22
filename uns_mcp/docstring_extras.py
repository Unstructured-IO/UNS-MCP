# Source of complete documentation:
#  https://docs.unstructured.io/api-reference/workflow/workflows
custom_nodes_settings_documentation = """
Custom workflow DAG nodes
- If WorkflowType is set to custom, you must also specify the settings for the workflow’s
directed acyclic graph (DAG) nodes. These nodes’ settings are specified in the workflow_nodes array.
- A Source node is automatically created when you specify the source_id value outside of the
workflow_nodes array.
- A Destination node is automatically created when you specify the destination_id value outside
of the workflow_nodes array.
- You can specify Partitioner, Chunker, Prompter, and Embedder nodes.
- The order of the nodes in the workflow_nodes array will be the same order that these nodes appear
in the DAG, with the first node in the array added directly after the Source node.
The Destination node follows the last node in the array.
- Be sure to specify nodes in the allowed order. The following DAG placements are all allowed:
    - Source -> Partitioner -> Destination,
    - Source -> Partitioner -> Chunker -> Destination,
    - Source -> Partitioner -> Chunker -> Embedder -> Destination,
    - Source -> Partitioner -> Prompter -> Chunker -> Destination,
    - Source -> Partitioner -> Prompter -> Chunker -> Embedder -> Destination

Partitioner node
A Partitioner node has a type of partition and a subtype of auto, vlm, hi_res, or fast.

Examples:
- auto strategy:
{
    "name": "Partitioner",
    "type": "partition",
    "subtype": "vlm",
    "settings": {
        "provider": "anthropic", (required)
        "model": "claude-3-5-sonnet-20241022", (required)
        "output_format": "text/html",
        "user_prompt": null,
        "format_html": true,
        "unique_element_ids": true,
        "is_dynamic": true,
        "allow_fast": true
    }
}

- vlm strategy:
    Allowed values are provider and model. Below are examples:
        - "provider": "anthropic" "model": "claude-3-5-sonnet-20241022",
        - "provider": "openai" "model": "gpt-4o"


- hi_res strategy:
{
    "name": "Partitioner",
    "type": "partition",
    "subtype": "unstructured_api",
    "settings": {
        "strategy": "hi_res",
        "include_page_breaks": <true|false>,
        "pdf_infer_table_structure": <true|false>,
        "exclude_elements": [
            "<element-name>",
            "<element-name>"
        ],
        "xml_keep_tags": <true|false>,
        "encoding": "<encoding>",
        "ocr_languages": [
            "<language>",
            "<language>"
        ],
        "extract_image_block_types": [
            "image",
            "table"
        ],
        "infer_table_structure": <true|false>
    }
}
- fast strategy
{
    "name": "Partitioner",
    "type": "partition",
    "subtype": "unstructured_api",
    "settings": {
        "strategy": "fast",
        "include_page_breaks": <true|false>,
        "pdf_infer_table_structure": <true|false>,
        "exclude_elements": [
            "<element-name>",
            "<element-name>"
        ],
        "xml_keep_tags": <true|false>,
        "encoding": "<encoding>",
        "ocr_languages": [
            "<language-code>",
            "<language-code>"
        ],
        "extract_image_block_types": [
            "image",
            "table"
        ],
        "infer_table_structure": <true|false>
    }
}


Chunker node
A Chunker node has a type of chunk and subtype of chunk_by_character or chunk_by_title.

- chunk_by_character
{
    "name": "Chunker",
    "type": "chunk",
    "subtype": "chunk_by_character",
    "settings": {
        "include_orig_elements": <true|false>,
        "new_after_n_chars": <new-after-n-chars>, (required, if not provided
set same as max_characters)
        "max_characters": <max-characters>, (required)
        "overlap": <overlap>, (required, if not provided set default to 0)
        "overlap_all": <true|false>,
        "contextual_chunking_strategy": "v1"
    }
}

- chunk_by_title
{
    "name": "Chunker",
    "type": "chunk",
    "subtype": "chunk_by_title",
    "settings": {
        "multipage_sections": <true|false>,
        "combine_text_under_n_chars": <combine-text-under-n-chars>,
        "include_orig_elements": <true|false>,
        "new_after_n_chars": <new-after-n-chars>,  (required, if not provided
set same as max_characters)
        "max_characters": <max-characters>, (required)
        "overlap": <overlap>,  (required, if not provided set default to 0)
        "overlap_all": <true|false>,
        "contextual_chunking_strategy": "v1"
    }
}


Prompter node
An Prompter node has a type of prompter and subtype of:
- openai_image_description,
- anthropic_image_description,
- bedrock_image_description,
- vertexai_image_description,
- openai_table_description,
- anthropic_table_description,
- bedrock_table_description,
- vertexai_table_description,
- openai_table2html,
- openai_ner

Example:
{
    "name": "Prompter",
    "type": "prompter",
    "subtype": "<subtype>",
    "settings": {}
}


Embedder node
An Embedder node has a type of embed

Allowed values for subtype and model_name include:

- "subtype": "azure_openai"
    - "model_name": "text-embedding-3-small"
    - "model_name": "text-embedding-3-large"
    - "model_name": "text-embedding-ada-002"
- "subtype": "bedrock"
    - "model_name": "amazon.titan-embed-text-v2:0"
    - "model_name": "amazon.titan-embed-text-v1"
    - "model_name": "amazon.titan-embed-image-v1"
    - "model_name": "cohere.embed-english-v3"
    - "model_name": "cohere.embed-multilingual-v3"
- "subtype": "togetherai":
    - "model_name": "togethercomputer/m2-bert-80M-2k-retrieval"
    - "model_name": "togethercomputer/m2-bert-80M-8k-retrieval"
    - "model_name": "togethercomputer/m2-bert-80M-32k-retrieval"

Example:
{
    "name": "Embedder",
    "type": "embed",
    "subtype": "<subtype>",
    "settings": {
        "model_name": "<model-name>"
    }
}
"""


def add_custom_node_examples(func):
    if func.__doc__ is None:
        func.__doc__ = ""
    func.__doc__ += "\n" + custom_nodes_settings_documentation
    return func
