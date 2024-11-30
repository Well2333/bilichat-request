from bilichat_request.account import get_web_account
from bilichat_request.render.column import screenshot as column_screenshot
from bilichat_request.render.dynamic import screenshot as dynamic_screenshot
from bilichat_request.render.video.style_blue import screenshot as video_screenshot
import asyncio
import json


async def test_request():
    async with get_web_account() as web_account:
        resp = await web_account.web_requester.get_user_dynamics(382666849)
        with open("temp/test.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(resp))


async def test_column_shot():
    picture = await column_screenshot("2")
    with open("temp/test.jpg", "wb") as f:
        f.write(picture)
        
async def test_dynamic_shot():
    picture = await dynamic_screenshot("1002987576472109056")
    with open("temp/test.jpg", "wb") as f:
        f.write(picture)
        
async def test_video_shot():   
    picture = await video_screenshot("BV1BfznYhE1M")
    with open("temp/test.jpg", "wb") as f:
        f.write(picture)     


loop = asyncio.get_event_loop()
loop.run_until_complete(test_video_shot())
