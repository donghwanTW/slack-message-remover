#!python3
import sys

from slack_sdk import WebClient

from slack_message_remover import *


def main() -> int:
    client = WebClient(token=token)
    messages = fetch_recent_messages(client)
    keywords = read_keywords_from_file()
    logger.info("Deleting messages containing the following strings:\n - " + "\n - ".join(keywords))
    try:
        while delete_message_include_keywords(client, messages, keywords):
            messages = fetch_recent_messages(client)
    except KeyboardInterrupt:
        logger.info("Stop to delete messages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
