import logging
import os
import uuid
from collections import Counter

from azure.cosmos import CosmosClient

logger = logging.getLogger("tiingobot_logger")


def db_connection():
    client = CosmosClient(os.environ['COSMOS_URI'], credential=os.environ['COSMOS_KEY'])
    database = client.get_database_client(os.environ['DATABASE_NAME'])
    container = database.get_container_client(os.environ['CONTAINER_NAME'])
    return container


# giver is not a string, not sure what it is
def give_sparkle(giver: str, receiver: str) -> str:

    giver = str(giver)
    container = db_connection()

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


def get_leaderboard() -> str:
    container = db_connection()
    response = "✨✨  Sparkle Leaderboard  ✨✨\n"
    results = container.query_items(
            query='SELECT sparkledb.receiver FROM sparkledb',
            enable_cross_partition_query=True)
    results = Counter(x['receiver'] for x in results).most_common()[0:3]
    for result in results:
        response += f"`@{result[0]}` has ✨✨{result[1]}✨✨\n"
    return response
