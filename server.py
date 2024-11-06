import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import Session, Ad, close_orm, init_orm

app = web.Application()

async def orm_context(app):
    print("START")
    await init_orm()
    yield
    await close_orm()
    print("FINISH")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response

app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def get_http_error(error_cls, error_msg):
    error = error_cls(
        text=json.dumps(
            {
                "error": error_msg,
            },
        ),
        content_type="application/json",
    )
    return error


async def get_ad_by_id(session: AsyncSession, ad_id: int) -> Ad:
    ad = await session.get(Ad, ad_id)
    if ad is None:
        raise get_http_error(web.HTTPNotFound, "ad not found")
    return ad


async def add_ad(session: AsyncSession, ad: Ad):
    session.add(ad)
    try:
        await session.commit()
    except IntegrityError:
        raise get_http_error(web.HTTPConflict, "ad already exist")
    return ad


class AdView(web.View):

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    @property
    def ad_id(self):
        return int(self.request.match_info["ad_id"])

    async def get(self):
        ad = await get_ad_by_id(self.session, self.ad_id)
        return web.json_response(ad.json)

    async def post(self):
        json_data = await self.request.json()
        ad = Ad(**json_data)
        ad = await add_ad(self.session, ad)
        return web.json_response({"id": ad.id})

    async def patch(self):
        json_data = await self.request.json()
        ad = await get_ad_by_id(self.session, self.ad_id)
        for field, value in json_data.items():
            setattr(ad, field, value)
        ad = await add_ad(self.session, ad)
        return web.json_response({"id": ad.id})

    async def delete(self):
        ad = await get_ad_by_id(self.session, self.ad_id)
        await self.session.delete(ad)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


app.add_routes(
    [
        web.get("/ad/{ad_id:\d+}", AdView),
        web.patch("/ad/{ad_id:\d+}", AdView),
        web.delete("/ad/{ad_id:\d+}", AdView),
        web.post("/ad/", AdView),
    ]
)

if __name__ == "__main__":
    web.run_app(app)
