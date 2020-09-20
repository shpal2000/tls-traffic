from fastapi import FastAPI
from typing import Optional, List
from pydantic import BaseModel

from fastapi.responses import HTMLResponse


import asyncio
import uvicorn


app = FastAPI()

class StopParam(BaseModel):
    timeout: int

@app.get('/', response_class=HTMLResponse)
async def root():
    reader, writer = await asyncio.open_connection('www.site.com'
                                                    , 80
                                                    , ssl=False)
    writer.write(f'GET / HTTP/1.1\r\nHost: www.site.com\r\n\r\n'.encode())
    await writer.drain()

    response = await reader.read (10000)

    writer.close()
    await writer.wait_closed()

    return HTMLResponse(content=response, status_code=200)

@app.post('/abort')
async def abort():
    return {}

@app.post('/stop')
async def stop(params : StopParam):
    return params


if __name__ == '__main__':
    asyncio.run (uvicorn.run(app
                                , host='0.0.0.0'
                                , port=8000
                                , loop='asyncio'
                                , debug=False))