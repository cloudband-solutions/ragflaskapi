from dataclasses import dataclass

import boto3


class StorageError(Exception):
    pass


class BaseStorageService:
    def save(self, key, data, content_type=None):
        raise NotImplementedError

    def read(self, key):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def url(self, key, expires_in=3600):
        raise NotImplementedError


@dataclass
@dataclass
class AmazonStorageService(BaseStorageService):
    bucket: str
    region: str
    access_key_id: str
    secret_access_key: str
    endpoint_url: str | None = None
    prefix: str | None = None

    def __post_init__(self):
        if not self.bucket:
            raise StorageError("AWS_S3_BUCKET is required for amazon storage")
        self._client = boto3.client(
            "s3",
            region_name=self.region or None,
            aws_access_key_id=self.access_key_id or None,
            aws_secret_access_key=self.secret_access_key or None,
            endpoint_url=self.endpoint_url or None,
        )

    def _object_key(self, key):
        key = key.lstrip("/")
        if self.prefix:
            return f"{self.prefix.rstrip('/')}/{key}"
        return key

    def save(self, key, data, content_type=None):
        object_key = self._object_key(key)
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        if hasattr(data, "read"):
            self._client.upload_fileobj(data, self.bucket, object_key, ExtraArgs=extra_args or None)
        else:
            params = {"Bucket": self.bucket, "Key": object_key, "Body": data}
            params.update(extra_args)
            self._client.put_object(**params)

    def read(self, key):
        object_key = self._object_key(key)
        response = self._client.get_object(Bucket=self.bucket, Key=object_key)
        return response["Body"].read()

    def delete(self, key):
        object_key = self._object_key(key)
        self._client.delete_object(Bucket=self.bucket, Key=object_key)

    def url(self, key, expires_in=3600):
        object_key = self._object_key(key)
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": object_key},
            ExpiresIn=expires_in,
        )
