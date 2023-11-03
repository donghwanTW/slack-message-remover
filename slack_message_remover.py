import logging
import os
import time
from typing import Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import dotenv_values

logging.basicConfig(
    format="{asctime} {levelname} {name}: {message}",
    style="{",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

config = dotenv_values(".env")
token = config.get("SLACK_BOT_TOKEN") or os.environ.get("SLACK_BOT_TOKEN")
channel_id = config.get("CHANNEL_ID") or os.environ.get("CHANNEL_ID")


def fetch_recent_messages(client: "WebClient") -> list[dict]:
    try:
        result = client.conversations_history(channel=channel_id, inclusive=True, limit=1000)
    except SlackApiError:
        logger.exception("Failed to read messages.")
        return []
    else:
        return result["messages"]


def read_keywords_from_file(filename: str = "keywords.txt") -> list[str]:
    with open(filename) as keywords:
        lines = keywords.readlines()
    lines_without_comments = [line[:-1] for line in lines if not line.startswith("#")]
    return lines_without_comments


def extract_text_from_slack_message(message: dict[str, Any]) -> None | str:
    if attachments := message.get("attachments"):
        return attachments[0]["text"]
    else:
        return None


def contains_keyword(text: None | str, keywords: list[str]) -> bool:
    if not text:
        return False
    for keyword in keywords:
        if keyword in text:
            return True
    return False


def delete_message(client: "WebClient", message: dict) -> bool:
    try:
        result = client.chat_delete(channel=channel_id, ts=message["ts"])
        logger.debug(result)
        return True
    except SlackApiError as e:
        logger.error(f"Failed to delete message: {e}")
        return False


def delete_message_include_keywords(client: "WebClient", messages: dict, keywords: list[str]) -> int:
    deleted_count = 0
    for message in messages:
        text = extract_text_from_slack_message(message)
        if contains_keyword(text, keywords):
            logger.info(message["text"])
            if delete_message(client, message):
                deleted_count += 1
                time.sleep(1.2)
    return deleted_count
