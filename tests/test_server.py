import anyio
from unittest.mock import patch

from mcp import Client
from src.server import mcp


def make_instance(instance_id, name=None):
    instance = {
        "InstanceId": instance_id,
        "InstanceType": "t2.micro",
        "State": {"Name": "running"},
        "Placement": {
            "AvailabilityZone": "us-east-1a"
        },
        "PrivateIpAddress": "10.0.1.25",
    }

    if name:
        instance["Tags"] = [
            {"Key": "Name", "Value": name}
        ]

    return instance


async def call_with_mocked_pages(client, pages):
    with patch("src.server.boto3.Session") as mock_session:

        session = mock_session.return_value
        session.region_name = None

        ec2 = session.client.return_value
        paginator = ec2.get_paginator.return_value
        paginator.paginate.return_value = pages

        result = await client.call_tool(
            "list_ec2_instances",
            {"region": "us-east-1"},
        )

        assert not result.is_error

        return result.structured_content


async def test_ec2_tool():

    async with Client(mcp, raise_exceptions=True) as client:

        # Test 1: Normal EC2 response
        pages = [
            {
                "Reservations": [
                    {
                        "Instances": [
                            make_instance(
                                "i-0123456789abcdef0",
                                "Test-Server",
                            )
                        ]
                    }
                ]
            }
        ]

        data = await call_with_mocked_pages(client, pages)

        assert data["total_instances"] == 1
        assert data["instances"][0]["name"] == "Test-Server"

        print("PASS: Normal EC2 response")

        # Test 2: No EC2 instances
        pages = [
            {"Reservations": []}
        ]

        data = await call_with_mocked_pages(client, pages)

        assert data["total_instances"] == 0
        assert data["instances"] == []

        print("PASS: Empty EC2 response")

        # Test 3: Instance without a Name tag
        pages = [
            {
                "Reservations": [
                    {
                        "Instances": [
                            make_instance("i-abcdef1234567890")
                        ]
                    }
                ]
            }
        ]

        data = await call_with_mocked_pages(client, pages)

        assert data["total_instances"] == 1
        assert data["instances"][0]["name"] == "Unnamed"

        print("PASS: Missing Name tag")

        # Test 4: Multiple EC2 response pages
        pages = [
            {
                "Reservations": [
                    {
                        "Instances": [
                            make_instance(
                                "i-11111111111111111",
                                "First-Server",
                            )
                        ]
                    }
                ]
            },
            {
                "Reservations": [
                    {
                        "Instances": [
                            make_instance(
                                "i-22222222222222222",
                                "Second-Server",
                            )
                        ]
                    }
                ]
            },
        ]

        data = await call_with_mocked_pages(client, pages)

        assert data["total_instances"] == 2
        assert len(data["instances"]) == 2
        assert data["instances"][0]["name"] == "First-Server"
        assert data["instances"][1]["name"] == "Second-Server"

        print("PASS: Multiple response pages")

    print("\nALL EC2 TESTS PASSED!")


if __name__ == "__main__":
    anyio.run(test_ec2_tool)
