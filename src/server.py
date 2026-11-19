
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from typing import Any

from mcp.server import MCPServer


mcp = MCPServer("AWS EC2 Read-Only Server")


@mcp.tool()
def list_ec2_instances(region: str | None = None) -> dict[str, Any]:
    """List EC2 instances and their basic details in an AWS region.

    This tool only reads information. It does not modify EC2 resources.
    """

    session = boto3.Session()
    selected_region = region or session.region_name

    if not selected_region:
        raise ValueError(
            "No AWS region configured. Configure a default region "
            "or provide one when calling this tool."
        )

    ec2 = session.client("ec2", region_name=selected_region)

    instances = []

    try:
        paginator = ec2.get_paginator("describe_instances")

        for page in paginator.paginate():
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    name = next(
                        (
                            tag["Value"]
                            for tag in instance.get("Tags", [])
                            if tag["Key"] == "Name"
                        ),
                        "Unnamed",
                    )

                    instances.append(
                        {
                            "name": name,
                            "instance_id": instance["InstanceId"],
                            "instance_type": instance["InstanceType"],
                            "state": instance["State"]["Name"],
                            "availability_zone": instance["Placement"][
                                "AvailabilityZone"
                            ],
                            "private_ip": instance.get("PrivateIpAddress"),
                        }
                    )

    except (ClientError, BotoCoreError) as error:
        raise RuntimeError(
            f"Unable to retrieve EC2 instances: {error}"
        ) from error

    return {
        "region": selected_region,
        "total_instances": len(instances),
        "instances": instances,
    }


if __name__ == "__main__":
    mcp.run()

