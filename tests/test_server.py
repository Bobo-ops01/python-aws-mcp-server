
import anyio
from unittest.mock import patch

from mcp import Client
from src.server import mcp


async def test_ec2_tool():
    with patch("src.server.boto3.Session") as mock_session:

        session = mock_session.return_value
        session.region_name = None

        ec2 = session.client.return_value
        paginator = ec2.get_paginator.return_value

        # Simulated EC2 response
        paginator.paginate.return_value = [
            {
                "Reservations": [
                    {
                        "Instances": [
                            {
                                "InstanceId": "i-0123456789abcdef0",
                                "InstanceType": "t2.micro",
                                "State": {"Name": "running"},
                                "Placement": {
                                    "AvailabilityZone": "us-east-1a"
                                },
                                "PrivateIpAddress": "10.0.1.25",
                                "Tags": [
                                    {"Key": "Name", "Value": "Test-Server"}
                                ],
                            }
                        ]
                    }
                ]
            }
        ]

        async with Client(mcp, raise_exceptions=True) as client:

            result = await client.call_tool(
                "list_ec2_instances",
                {"region": "us-east-1"},
            )

        assert not result.is_error

        data = result.structured_content

        assert data["total_instances"] == 1
        assert data["instances"][0]["name"] == "Test-Server"

        print("\nEC2 TOOL EXECUTION SUCCESSFUL")
        print(data)


if __name__ == "__main__":
    anyio.run(test_ec2_tool)

