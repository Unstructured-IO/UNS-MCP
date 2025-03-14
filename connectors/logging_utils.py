from typing import Literal

from unstructured_client.models.shared import (
    SourceConnectorInformation, AzureSourceConnectorConfig
)


def create_log_for_created_updated_connector(response, source_name: str,
                                             source_or_destination: Literal[
                                                 'Source', 'Destination'],
                                             created_or_updated: Literal[
                                                 'Created', "Updated"]) -> str:
    info: SourceConnectorInformation | None = response.source_connector_information
    config: AzureSourceConnectorConfig | None = response.source_connector_config if info else None

    result = [f"{source_name} {source_or_destination} Connector {created_or_updated}:"]

    if info:
        result.extend([f"Name: {info.name}", f"ID: {info.id}"])

    if config:
        result.extend(["Configuration:", '  remote_url: {config.remote_url}',
                       '  recursive: {config.recursive}'])

    combined_result = "\n".join(result)
    return combined_result
