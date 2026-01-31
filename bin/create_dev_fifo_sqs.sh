#!/usr/bin/env bash

set -euo pipefail

# Allow overriding the Localstack endpoint via LOCALSTACK_URL to keep this script flexible.
LOCALSTACK_URL="${LOCALSTACK_URL:-http://localhost:4566}"

# Allow passing a queue name; default to our report queue with the required FIFO suffix.
QUEUE_NAME="${1:-ragflaskapi_queue.fifo}"

aws --endpoint-url="${LOCALSTACK_URL}" sqs create-queue \
  --queue-name "${QUEUE_NAME}" \
  --attributes FifoQueue=true,ContentBasedDeduplication=true
