# Oracle Node Client

The Oracle Node Client is a Python application that acts as an oracle node, providing data query and data submission capabilities to clients. It interacts with a Redis database and communicates with external systems, such as an LND instance.

## Prerequisites

Before running the Oracle Node Client, ensure that you have the following prerequisites installed:

- Docker: Install Docker
- Docker Compose: Install Docker Compose

## Running the Client

Start the Oracle Node Client and dependencies:

```sh
docker compose up --build
```

The client will start running, and you should see the logs in the console.

## Running Tests

To run the test suite for the Oracle Node Client, use the following command:

```sh
docker compose -f docker-compose.test.yml up --build
```

This command will build and start the test environment, execute the tests, and display the test results in the console.

## Usage

The Oracle Node Client exposes an HTTP API for interacting with the oracle node. The API documentation can be found in the [API Documentation](../../docs/oracle-node-api.md) file.

Make requests to the Oracle Node Client API using your preferred HTTP client, such as cURL or Postman.
