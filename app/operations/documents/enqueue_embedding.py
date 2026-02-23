import json
import os
import uuid

import boto3
from flask import current_app

from app import db


class EnqueueEmbedding:
    def __init__(self, document):
        self.document = document

    def execute(self):
        queue_url = current_app.config.get("SQS_QUEUE_URL") or os.getenv("SQS_QUEUE_URL")
        if not queue_url:
            self._mark_failed("SQS_QUEUE_URL is not configured.")
            return False

        payload = {
            "document_id": self.document.id,
            "name": self.document.name,
            "key": self.document.storage_key,
        }

        try:
            client = self._build_sqs_client()
            send_kwargs = {"QueueUrl": queue_url, "MessageBody": json.dumps(payload)}
            if queue_url.endswith(".fifo"):
                group_id = (
                    current_app.config.get("SQS_MESSAGE_GROUP_ID")
                    or os.getenv("SQS_MESSAGE_GROUP_ID")
                    or "embeddings"
                )
                send_kwargs["MessageGroupId"] = group_id
                dedup_id = (
                    current_app.config.get("SQS_MESSAGE_DEDUPLICATION_ID")
                    or os.getenv("SQS_MESSAGE_DEDUPLICATION_ID")
                )
                if not dedup_id:
                    dedup_id = f"{self.document.id}-{uuid.uuid4()}"
                send_kwargs["MessageDeduplicationId"] = dedup_id
            client.send_message(**send_kwargs)
            self.document.embedding_status = "pending"
            self.document.enqueue_error = None
            self.document.embedding_error = None
            db.session.commit()
            return True
        except Exception as exc:  # noqa: BLE001 - propagate error message to record
            self._mark_failed(str(exc))
            return False

    def _mark_failed(self, message):
        self.document.embedding_status = "failed"
        self.document.enqueue_error = message
        db.session.commit()

    def _build_sqs_client(self):
        region = current_app.config.get("SQS_REGION") or os.getenv("SQS_REGION") or None
        endpoint = current_app.config.get("AWS_SQS_ENDPOINT") or os.getenv(
            "AWS_SQS_ENDPOINT"
        )
        return boto3.client("sqs", region_name=region, endpoint_url=endpoint or None)
