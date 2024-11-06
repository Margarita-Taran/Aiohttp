import asyncio

import aiohttp


async def main():
    session = aiohttp.ClientSession()
    # response = await session.post("http://127.0.0.1:8080/ad/",
    #                              json={"title": "title_1", "description": "description_1", "owner": "owner_1"}
    #                              )
    # print(response.status)
    # print(await response.text())

    # response = await session.patch("http://127.0.0.1:8080/ad/1",
    #                              json={"title": "update_title_1", "description": "update_description_1"}
    #                              )
    # print(response.status)
    # print(await response.text())
    #
    # response = await session.get("http://127.0.0.1:8080/ad/1")
    # print(response.status)
    # print(await response.text())

    response = await session.delete("http://127.0.0.1:8080/ad/1")
    print(response.status)
    print(await response.text())

    response = await session.get("http://127.0.0.1:8080/ad/1")
    print(response.status)
    print(await response.text())

    await session.close()


asyncio.run(main())
