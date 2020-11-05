from aiohttp import web
import json

from .tgen.TlsApp import TlsApp

app = web.Application()

async def get_config(request):
    data_s = await request.read()
    data_j = json.loads(data_s)
    return web.json_response (TlsApp.get_config ('traffic_node.tgen'
                                , data_j['app_name']
                                , data_j['testbed']
                                , **data_j['app_params']))

async def start_run(request):
    data_s = await request.read()
    data_j = json.loads(data_s)
    TlsApp.start_run ('traffic_node.tgen'
                        , data_j['runid']
                        , data_j['app_config'])
    return web.json_response ({'status' : 0})

async def stop_run(request):
    data_s = await request.read()
    data_j = json.loads(data_s)
    TlsApp.stop_run (data_j['runid'])
    return web.json_response ({'status' : 0})


async def run_list(request):
    return web.json_response ({"run_list" : TlsApp.run_list()})


app.add_routes([web.get('/run_list', run_list),
                web.post('/stop_run', stop_run),
                web.post('/start_run', start_run),
                web.post('/get_config', get_config)])

if __name__ == '__main__':  
    web.run_app(app, port=8889)
