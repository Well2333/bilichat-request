from bilichat_request.config import NONEBOT_ENV

if NONEBOT_ENV:
    from nonebot_plugin_apscheduler import scheduler  # type: ignore

else:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduler = AsyncIOScheduler()