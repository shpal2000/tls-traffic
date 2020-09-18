from fastapi import FastAPI
from typing import Optional, List
from pydantic import BaseModel
from fastapi.responses import ORJSONResponse

app = FastAPI()

class StartTraffic(BaseModel):
    runid: str

class StartClientServer(StartTraffic):
    na: str
    nb: str
    client_mac_seed: str
    server_mac_seed: str
    cps: int
    max_pipeline: int
    max_active: int
    total_conn_count: int
    app_next_write: int
    app_cs_data_len: int


@app.post('/start_cps', response_class=ORJSONResponse)
async def start_cps(params : StartCPS
                    , settings: config.Settings = Depends (get_settings)):

    return params

@app.post('/stop', response_class=ORJSONResponse)
async def stop(params : StopReq
                , settings: config.Settings = Depends (get_settings)):

    crud.del_task(settings.db_file, params.runid)
    return params


