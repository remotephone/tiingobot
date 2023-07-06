import logging
import os
import uuid
from collections import Counter

from azure.cosmos import CosmosClient

logger = logging.getLogger("tiingobot_logger")


def db_connection():
    client = CosmosClient(os.environ["COSMOS_URI"], credential=os.environ["COSMOS_KEY"])
    database = client.get_database_client(os.environ["DATABASE_NAME"])
    container = database.get_container_client("complaints")
    return container


# giver is not a string, not sure what it is
def complaint_lodger(giver: str, receiver: str, complaint: str) -> str:
    try:
        giver = str(giver)
        container = db_connection()
    except Exception as e:
        logger.error(f"Failed to connect to db - {e}")
        return "There was an error lodging your complaint. Please try again later."
    try:
        container.upsert_item(
            {
                "id": str(uuid.uuid4()),
                "giver": giver,
                "receiver": receiver,
                "complaint": complaint,
            }
        )
        logger.info(f"@{giver} complained about @{receiver}")
    except Exception as e:
        logger.error(f"Error inserting complaint - {e}")
        return "Sorry there was a problem"

    for item in container.query_items(
        query=f'SELECT VALUE COUNT(1) FROM complaints WHERE complaints.receiver = "{receiver}"',
        enable_cross_partition_query=True,
    ):
        complaint_count = str(item)
        logger.info(f"Got {complaint_count} complaints for {receiver}")
        return f"😒😒 {receiver} has {complaint_count} complaints! 😒😒"
    return "oops, this code is busted"


def get_complaints_for_user(user: str) -> str:
    container = db_connection()
    response = f"😒😒  Complaints for {user}  😒😒\n"
    results = container.query_items(
        query=f"SELECT TOP 3 * FROM complaints where complaints.receiver = '{user}' ORDER BY complaints._ts desc",
        enable_cross_partition_query=True,
    )
    response = f"😒😒 Recent Complaints for {user}  😒😒\n"
    for result in results:
        response += f"- {result['complaint']}\n"
    return response
