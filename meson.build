libdl = meson.get_compiler('cpp').find_library('dl', required : true)

openssl = dependency('openssl')
nlohmann_json_proj = subproject('json')
nlohmann_json_dep = nlohmann_json_proj.get_variable('nlohmann_json_dep')
incdirs = include_directories(['../tlspack-socket/'])

subdir ('tls_client')
subdir ('tls_server')
subdir ('rpc_server')

executable('tlspack.exe'
            , sources : [ 'main.cpp', 'app.cpp' ]
            , dependencies: [openssl, nlohmann_json_dep, libdl]
            , include_directories : [incdirs]
            , link_with : [ev_socklib, rpc_serverlib]
            , build_rpath : '/usr/local/lib'
            , install_rpath : '/usr/local/lib'
            , install_dir : '/srcdir/imgdir/'
            , install : true)

