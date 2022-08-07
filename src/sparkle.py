import os
import uuid
import logging

from azure.cosmos import CosmosClient

logger = logging.getLogger("tiingobot_logger")


def give_sparkle(giver: str, receiver: str) -> str:
    client = CosmosClient(os.environ['COSMOS_URI'], credential=os.environ['COSMOS_KEY'])

    database = client.get_database_client(os.environ['DATABASE_NAME'])
    container = database.get_container_client(os.environ['CONTAINER_NAME'])
    try:
        container.upsert_item({
                'id': str(uuid.uuid4()),
                'giver': giver,
                'receiver': receiver
                }
        )
        logger.info(f"Inserted sparkle from @{giver} to @{receiver}")
    except Exception as e:
        logger.error(f"Error inserting sparkle - {e}")

    for item in container.query_items(
        query=f'SELECT VALUE COUNT(1) FROM sparkledb WHERE sparkledb.receiver = "{receiver}"',
        enable_cross_partition_query=True):
        sparkle_count = str(item)
        logger.info(f"Got {sparkle_count} sparkles for {receiver}")
    return f"✨✨ {receiver} has {sparkle_count} sparkles! ✨✨"
