import asyncio
import json

from bilichat_request.account import get_web_account
from bilichat_request.functions.render.column import screenshot as column_screenshot
from bilichat_request.functions.render.dynamic import screenshot as dynamic_screenshot
from bilichat_request.functions.render.video.style_blue import (
    screenshot as video_screenshot,
)


async def test_request():
    async with get_web_account() as web_account:
        resp = await web_account.web_requester.get_user_dynamics(382666849)
        with open("temp/req.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(resp))


async def test_column_shot():
    picture = await column_screenshot("2")
    with open("temp/col_test.jpg", "wb") as f:
        f.write(picture)


async def test_dynamic_shot():
    picture = await dynamic_screenshot("1002987576472109056")
    with open("temp/dyn_test.jpg", "wb") as f:
        f.write(picture)


async def test_video_shot():
    picture = await video_screenshot("BV1BfznyhE1M")
    with open("temp/vid_test.jpg", "wb") as f:
        f.write(picture)


# run all tests
loop = asyncio.get_event_loop()
loop.run_until_complete(test_request())
loop.run_until_complete(test_column_shot())
loop.run_until_complete(test_dynamic_shot())
# loop.run_until_complete(test_video_shot())
