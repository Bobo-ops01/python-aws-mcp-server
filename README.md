# Python AWS MCP Server

A Python-based Model Context Protocol (MCP) server exposing read-only AWS EC2 functionality.

## Features

The server provides the following MCP tool:

### list_ec2_instances

Lists EC2 instances in a specified AWS region and returns:

- Instance name
- Instance ID
- Instance type
- Instance state
- Availability Zone
- Private IP address

It uses Boto3 and the EC2 DescribeInstances API, including pagination.

The tool is read-only. It does not create, start, stop, or terminate EC2 instances.

## Technology Stack

- Python 3.12
- Model Context Protocol SDK
- Boto3
- AWS EC2

## Setup

Create a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install -r requirements.txt

## Run the Server

    python -m src.server

## Run the Tests

    python -m tests.test_server

The local execution test uses mocked EC2 data. It does not require AWS credentials or create AWS resources.

## AWS Permissions

For live AWS integration, the configured AWS identity requires:

    ec2:DescribeInstances

## Project Status

- [x] MCP server implemented
- [x] Read-only EC2 tool implemented
- [x] MCP tool discovery tested
- [x] Execution tested with mocked EC2 data
- [ ] Live AWS integration
- [ ] Additional AWS tools
