from aiohttp import web
import json
import os
import sys

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


async def purge_testbed(request):
    TlsApp.purge_testbed (request.query['testbed'])
    return web.json_response ({'status' : 0})


async def stop_run(request):
    TlsApp.stop_run (request.query['runid'])
    return web.json_response ({'status' : 0})


async def get_stats(request):
    return web.json_response (TlsApp.get_stats (request.query['runid']))


async def run_list(request):
    return web.json_response ({"run_list" : TlsApp.run_list()})


app.add_routes([web.get('/run_list', run_list),
                web.get('/get_stats', get_stats),
                web.get('/stop_run', stop_run),
                web.get('/purge_testbed', purge_testbed),
                web.post('/start_run', start_run),
                web.post('/get_config', get_config)])

if __name__ == '__main__':
    TlsApp.restart(sys.argv[1])
    web.run_app(app, port=8889)
