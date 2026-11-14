import json
import uuid
from datetime import datetime, timezone

from kafka import KafkaProducer
from kafka.errors import KafkaError

from config.settings import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC


def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        key_serializer=lambda value: value.encode("utf-8"),
        acks="all",
        retries=3,
    )


def publish_ingestion_request(payload):
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "ingest_filings",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "limit": payload["limit"],
    }

    producer = create_producer()

    try:
        producer.send(
            KAFKA_TOPIC,
            key=event["event_id"],
            value=event,
        ).get(timeout=15)
        producer.flush()
    except KafkaError:
        raise
    finally:
        producer.close()

    return event
