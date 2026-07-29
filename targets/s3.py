import os
import datetime
import boto3
from botocore.exceptions import ClientError
from core.models import Repo
from targets.base import Target


class S3Target(Target):
    def migrate(self, repo: Repo, temp_dir: str, tar_path: str):
        print(f"\n[MIGRATE s3] {repo.name}")

        bucket = os.getenv("S3_BUCKET")
        if not bucket:
            raise Exception("Falta S3_BUCKET en .env")

        s3 = self._get_client()

        key = self._build_key(repo, tar_path)

        self._upload(s3, bucket, key, tar_path)

    def _get_client(self):
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        return session.client("s3")

    def _build_key(self, repo: Repo, tar_path: str):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = os.path.basename(tar_path)
        if repo.s3_prefix:
            return f"{date}/{repo.s3_prefix}/{filename}"
        return f"{date}/{repo.name}/{filename}"

    def _upload(self, s3, bucket, key, file_path):
        try:
            print(f"Subiendo a s3://{bucket}/{key} ...")
            s3.upload_file(file_path, bucket, key)
            print("OK upload a S3")
        except ClientError as e:
            raise RuntimeError(f"Error subiendo a S3: {e}") from e
