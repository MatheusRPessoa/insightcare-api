from functools import lru_cache

import boto3
from botocore.config import Config

from app.core.config import settings


@lru_cache(maxsize=1)
def get_bedrock_client():
    session = boto3.Session(
        profile_name=settings.aws_profile,
        region_name=settings.aws_region,
    )

    return session.client(
        "bedrock-runtime",
        config=Config(
            connect_timeout=10,
            read_timeout=60,
            retries={"max_attempts": 2},
        ),
    )
