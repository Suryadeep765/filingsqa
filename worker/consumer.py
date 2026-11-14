import json
import logging
import time

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from config.settings import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_GROUP_ID,
    KAFKA_TOPIC,
)
from worker.ingestion import ingest_filings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


def create_consumer():
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )


def main():
    while True:
        try:
            consumer = create_consumer()
            logger.info("Listening for ingestion jobs on %s", KAFKA_TOPIC)

            try:
                for message in consumer:
                    event = message.value

                    if event.get("event_type") != "ingest_filings":
                        logger.warning("Skipping unknown event: %s", event)
                        consumer.commit()
                        continue

                    logger.info(
                        "Processing ingestion event %s",
                        event.get("event_id"),
                    )

                    try:
                        ingest_filings(int(event["limit"]))
                        consumer.commit()
                        logger.info(
                            "Completed ingestion event %s",
                            event.get("event_id"),
                        )
                    except Exception:
                        logger.exception(
                            "Ingestion failed for event %s; offset not committed",
                            event.get("event_id"),
                        )
                        raise
            finally:
                consumer.close()

        except (KafkaError, OSError):
            logger.exception("Kafka unavailable; retrying in 5 seconds")
            time.sleep(5)


if __name__ == "__main__":
    main()
