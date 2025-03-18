from typing import Literal


def create_log_for_created_updated_connector(
    response,
    connector_name: str,
    connector_type: Literal["Source", "Destination"],
    created_or_updated: Literal["Created", "Updated"],
) -> str:
    if connector_type == "Source":
        info = response.source_connector_information
    else:
        info = response.destination_connector_information

    result = [f"{connector_name} {connector_type} Connector {created_or_updated}:"]

    if info:
        result.extend([f"Name: {info.name}", f"ID: {info.id}"])

    # Note(tracy): let's not output creds config for now as different connectors come in
    # different creds name, logging them is not necessary anyway
    # if config:
    #     result.extend(
    #         [
    #             "Configuration:",
    #             "  remote_url: {config.remote_url}",
    #             "  recursive: {config.recursive}",
    #         ],
    #     )

    combined_result = "\n".join(result)
    return combined_result
