openssl = dependency('openssl')
nlohmann_json_proj = subproject('json')
nlohmann_json_dep = nlohmann_json_proj.get_variable('nlohmann_json_dep')
incdirs = include_directories(['../../tlspack-socket/', '../', '../../node/deps/llhttp/include'])

shared_library('ocsp_server_perf'
            , sources : [ './ocsp_server_perf.cpp'
                        , '../../node/deps/llhttp/src/api.c'
                        , '../../node/deps/llhttp/src/http.c'
                        , '../../node/deps/llhttp/src/llhttp.c']
            , dependencies: [openssl, nlohmann_json_dep]
            , include_directories : [incdirs]
            , link_with : ev_socklib
            , install_rpath : '/rundir/lib'
            , install_dir : '/srcdir/imgdir/'
            , install : true)

