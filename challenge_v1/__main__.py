import logging
import os

import requests

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IT_ROLL_ID = -218375169


def get_wall(count: int, offset: int) -> tuple[int, list[dict]]:
    """wall.get method."""
    resp = requests.get(
        "https://api.vk.com/method/wall.get",
        params={
            "owner_id": str(IT_ROLL_ID),
            "count": str(count),
            "offset": str(offset),
            "v": "5.199",
        },
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
        timeout=5,
    )
    json_resp = resp.json()
    count = json_resp["response"]["count"]
    items = json_resp["response"]["items"]
    return count, items


def get_comments(post_id: int) -> list[str]:
    """wall.getComments method."""
    resp = requests.get(
        "https://api.vk.com/method/wall.getComments",
        params={
            "owner_id": str(IT_ROLL_ID),
            "post_id": str(post_id),
            "v": "5.199",
        },
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
        timeout=5,
    )
    json_resp = resp.json()
    items = json_resp["response"]["items"]
    return [item["text"] for item in items]


def count_envelope(comment: str) -> int:
    """Count `энвилоуп` in the comment text."""
    return comment.lower().count("энвилоуп")


def main() -> None:
    """Entry point."""
    logging.basicConfig(level=logging.INFO)
    envelope_count = 0
    count = 1
    offset = 0
    while offset < count:
        count, items = get_wall(100, offset)
        for item in items:
            if item["comments"]["count"] > 0:
                comments = get_comments(item["id"])
                for comment in comments:
                    envelope_count += count_envelope(comment)
        offset += len(items)
        logging.info("Processed %d/%d posts", offset, count)
    print('Количество "энвилоуп" в комментариях:', envelope_count)


if __name__ == "__main__":
    main()
