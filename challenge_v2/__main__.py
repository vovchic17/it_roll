import asyncio
import os
import time
from typing import TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    from collections.abc import Coroutine

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IT_ROLL_ID = -218375169


async def request(
    session: aiohttp.ClientSession,
    method: str,
    **params: str | int,
) -> dict:
    """Make VK API request."""
    resp = await session.get(
        f"https://api.vk.com/method/{method}",
        params={
            **params,
            "v": "5.199",
        },
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )
    return await resp.json()


async def get_posts_count(session: aiohttp.ClientSession) -> int:
    """Get community posts count."""
    json_resp = await request(
        session,
        "wall.get",
        owner_id=IT_ROLL_ID,
        count=1,
    )
    return json_resp["response"]["count"]


async def get_posts_with_comments(
    session: aiohttp.ClientSession,
    count: int,
    offset: int,
) -> list:
    """Get community posts that have at least 1 comment."""
    json_resp = await request(
        session,
        "wall.get",
        owner_id=IT_ROLL_ID,
        count=count,
        offset=offset,
    )
    items = json_resp["response"]["items"]
    return [item["id"] for item in items if item["comments"]["count"] > 0]


async def get_post_envelope_count(
    session: aiohttp.ClientSession,
    post_id: int,
) -> int:
    """Get post envelope count."""
    json_resp = await request(
        session,
        "wall.getComments",
        owner_id=IT_ROLL_ID,
        post_id=post_id,
    )
    comments = json_resp["response"]["items"]
    return sum(
        comment["text"].lower().count("энвилоуп") for comment in comments
    )


async def main() -> None:
    """Entry point."""
    start = time.perf_counter()
    step = 20
    async with aiohttp.ClientSession() as session:
        posts_count = await get_posts_count(session)
        tasks: list[Coroutine] = [
            get_posts_with_comments(session, step, i)
            for i in range(0, posts_count, step)
        ]
        results = await asyncio.gather(*tasks)

        tasks = [
            get_post_envelope_count(session, post)
            for post in [_ for _ in results for _ in _]
        ]
        envelope_count = sum(await asyncio.gather(*tasks))

    end = time.perf_counter()

    print('Количество "энвилоуп" в комментариях:', envelope_count)
    print(f"Время, затраченное на подсчёт энвилоупов: {end - start:.3f} с")


if __name__ == "__main__":
    asyncio.run(main())
