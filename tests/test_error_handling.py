import unittest
from unittest.mock import patch

from botocore.exceptions import ClientError, EndpointConnectionError

from src.server import list_ec2_instances


class TestEC2ErrorHandling(unittest.TestCase):

    def test_missing_region(self):
        with patch("src.server.boto3.Session") as mock_session:
            mock_session.return_value.region_name = None

            with self.assertRaisesRegex(
                ValueError, "No AWS region configured"
            ):
                list_ec2_instances()

        print("PASS: Missing AWS region")

    def test_access_denied(self):
        with patch("src.server.boto3.Session") as mock_session:
            session = mock_session.return_value
            session.region_name = None

            paginator = (
                session.client.return_value
                .get_paginator.return_value
            )

            paginator.paginate.side_effect = ClientError(
                {
                    "Error": {
                        "Code": "AccessDenied",
                        "Message": "Not authorized",
                    }
                },
                "DescribeInstances",
            )

            with self.assertRaisesRegex(
                PermissionError, "ec2:DescribeInstances"
            ):
                list_ec2_instances("us-east-1")

        print("PASS: AWS access denied")

    def test_aws_api_failure(self):
        with patch("src.server.boto3.Session") as mock_session:
            session = mock_session.return_value
            session.region_name = None

            paginator = (
                session.client.return_value
                .get_paginator.return_value
            )

            paginator.paginate.side_effect = ClientError(
                {
                    "Error": {
                        "Code": "ServiceUnavailable",
                        "Message": "Service unavailable",
                    }
                },
                "DescribeInstances",
            )

            with self.assertRaisesRegex(
                RuntimeError, "ServiceUnavailable"
            ):
                list_ec2_instances("us-east-1")

        print("PASS: AWS API failure")

    def test_connection_failure(self):
        with patch("src.server.boto3.Session") as mock_session:
            session = mock_session.return_value
            session.region_name = None

            paginator = (
                session.client.return_value
                .get_paginator.return_value
            )

            paginator.paginate.side_effect = EndpointConnectionError(
                endpoint_url="https://ec2.us-east-1.amazonaws.com"
            )

            with self.assertRaisesRegex(
                RuntimeError, "Unable to configure or communicate"
            ):
                list_ec2_instances("us-east-1")

        print("PASS: AWS connection failure")


if __name__ == "__main__":
    unittest.main(verbosity=2)
