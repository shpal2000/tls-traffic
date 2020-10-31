openssl = dependency('openssl')
nlohmann_json_proj = subproject('json')
nlohmann_json_dep = nlohmann_json_proj.get_variable('nlohmann_json_dep')
incdirs = include_directories(['../../tlspack-socket/', '../'])

rpc_serverlib = shared_library('rpc_server'
                                , sources : [ './rpc_server.cpp']
                                , dependencies: [openssl, nlohmann_json_dep]
                                , include_directories : [incdirs]
                                , link_with : ev_socklib
                                , install : false)

