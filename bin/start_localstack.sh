#!/usr/bin/env bash
set -euo pipefail

# Load token securely
source "$HOME/.localstack.env"

docker run --rm \
  -p 4566:4566 \
  -e LOCALSTACK_AUTH_TOKEN \
  -e SERVICES=s3,sqs \
  localstack/localstack
