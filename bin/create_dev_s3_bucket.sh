#!/usr/bin/env bash

set -euo pipefail

# Allow overriding the Localstack endpoint via LOCALSTACK_URL to keep this script flexible.
LOCALSTACK_URL="${LOCALSTACK_URL:-http://localhost:4566}"

# Use AWS_REGION/AWS_DEFAULT_REGION if set; default to ap-southeast-1.
AWS_REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-ap-southeast-1}}"

# Allow overriding the bucket name via S3_BUCKET_NAME; default to our documents bucket.
# S3 bucket names must be lowercase and cannot include underscores.
S3_BUCKET_NAME="${S3_BUCKET_NAME:-ragflaskapi-documents}"

echo "Creating bucket $S3_BUCKET_NAME"

if aws --endpoint-url="${LOCALSTACK_URL}" s3api head-bucket \
  --bucket "${S3_BUCKET_NAME}" \
  --region "${AWS_REGION}" >/dev/null 2>&1; then
  echo "Bucket ${S3_BUCKET_NAME} already exists; skipping create."
  echo "Listing buckets in Localstack"
  aws --endpoint-url="${LOCALSTACK_URL}" s3api list-buckets \
    --region "${AWS_REGION}"
else
  if [[ "${AWS_REGION}" == "us-east-1" ]]; then
    aws --endpoint-url="${LOCALSTACK_URL}" s3api create-bucket \
      --bucket "${S3_BUCKET_NAME}" \
      --region "${AWS_REGION}"
  else
    aws --endpoint-url="${LOCALSTACK_URL}" s3api create-bucket \
      --bucket "${S3_BUCKET_NAME}" \
      --region "${AWS_REGION}" \
      --create-bucket-configuration LocationConstraint="${AWS_REGION}"
  fi
fi
