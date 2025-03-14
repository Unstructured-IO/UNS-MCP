from typing import Literal

from unstructured_client.models.shared import (
    SourceConnectorInformation, AzureSourceConnectorConfig, SourceConnectorInformationConfig
)


def create_log_for_created_updated_source_connector(response, source_name: str,
                                                    created_or_updated: Literal[
                                                 'Created', "Updated"]) -> str:
    info: SourceConnectorInformation | None = response.source_connector_information
    config: SourceConnectorInformationConfig | None = response.config if info else None

    result = [f"{source_name} Source Connector {created_or_updated}:"]

    if info:
        result.extend([f"Name: {info.name}", f"ID: {info.id}"])

    if config:
        result.extend(["Configuration:", '  remote_url: {config.remote_url}',
                       '  recursive: {config.recursive}'])

    combined_result = "\n".join(result)
    return combined_result
