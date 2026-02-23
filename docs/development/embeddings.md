# Embedding workflow

## Status tracking
Each `documents` record tracks its embedding lifecycle:
- `embedding_status`: `pending`, `processing`, `embedded`, or `failed`
- `enqueue_error`: set when the document could not be queued to SQS
- `embedding_error`: set when the worker failed during embedding

## Filtering by status
Both `GET /documents` and `GET /public/documents` accept `embedding_status`:
```
/documents?embedding_status=embedded
/public/documents?embedding_status=failed
```
Accepted values: `pending`, `processing`, `embedded`, `failed`.

## Enqueue behavior
- On upload, the API enqueues an SQS job with `{ document_id, name, key }`.
- If enqueue fails, `embedding_status` is set to `failed` and `enqueue_error` is recorded.

## Retry failed enqueue
Use the retry endpoint to re-queue a failed document:
```bash
POST /documents/<document_id>/enqueue
```

Behavior:
- Returns `404` if the document does not exist.
- Returns `422` if the document is not in `failed` status.
- On success, clears `enqueue_error` and sets `embedding_status` to `pending`.
