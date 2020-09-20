from fastapi import FastAPI
from typing import Optional, List
from pydantic import BaseModel

import asyncio
import uvicorn
import json
import sys


app = FastAPI()

class BaseParam(BaseModel):
    rpc_ip: str
    rpc_port: int

class StopParam(BaseParam):
    timeout: int

class EvSockStatsParam(BaseParam):
    stats_group: str

@app.post('/start')
async def start():
    return {}

@app.post('/abort')
async def abort():
    return {}

@app.post('/stop')
async def stop(params : StopParam):
    return params

@app.get('/ev_sockstats')
async def ev_sockstats(params : EvSockStatsParam):
    reader, writer = await asyncio.open_connection (params.rpc_ip
                                                    , params.rpc_port
                                                    , ssl=False)

    writer.write('{"cmd" : "get_ev_sockstats"}'.encode())
    await writer.drain()

    response = await reader.read (-1)

    writer.close()
    await writer.wait_closed()

    return json.loads (response)

if __name__ == '__main__':
    rpc_proxy_ip = sys.argv[1]
    rpc_proxy_port = int(sys.argv[2])
    asyncio.run (uvicorn.run(app
                                , host=rpc_proxy_ip
                                , port=rpc_proxy_port
                                , loop='asyncio'
                                , debug=False))