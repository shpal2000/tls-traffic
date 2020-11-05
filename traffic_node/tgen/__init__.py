__author__ = 'Shirish Pal'

def start (app_name, testbed, runid, **app_kwargs):
    from .TlsApp import TlsApp
    return TlsApp.start (__name__, app_name, testbed, runid, **app_kwargs)
  
def stop (runid):
    from .TlsApp import TlsApp
    TlsApp.stop_run (runid)

def stats_iter (runid):
    from .TlsApp import TlsApp
    return TlsApp.stats_iter (runid)

def purge_testbed (testbed):
    from .TlsApp import TlsApp
    TlsApp.purge_testbed (testbed)

def run_list ():
    from .TlsApp import TlsApp
    return TlsApp.run_list ()