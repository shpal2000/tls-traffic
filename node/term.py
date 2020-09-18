__author__ = 'Shirish Pal'

import os
import subprocess
import sys
import argparse
import json
import jinja2
import time
from threading import Thread
import pdb

supported_ciphers = [
    {'cipher_name' : 'AES128-SHA',
        'cipher' : '{AES128-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '10.2',
        'server_ip_prefix' : '100.2'
        },

    {'cipher_name' : 'AES256-SHA',
        'cipher' : '{AES256-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '11.2',
        'server_ip_prefix' : '101.2'
        },

    {'cipher_name' : 'DHE-RSA-AES128-SHA',
        'cipher' : '{DHE-RSA-AES128-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '12.2',
        'server_ip_prefix' : '102.2'
        },

    {'cipher_name' : 'DHE-RSA-AES256-SHA',
        'cipher' : '{DHE-RSA-AES256-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '13.2',
        'server_ip_prefix' : '103.2'
        },

    {'cipher_name' : 'DHE-RSA-AES128-GCM-SHA256',
        'cipher' : '{DHE-RSA-AES128-GCM-SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '14.2',
        'server_ip_prefix' : '104.2'
        },

    {'cipher_name' : 'ECDHE-ECDSA-AES128-SHA',
        'cipher' : '{ECDHE-ECDSA-AES128-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server2.cert',
        'srv_key' : '/rundir/certs/server2.key',
        'client_ip_prefix' : '15.2',
        'server_ip_prefix' : '105.2'
        },

    {'cipher_name' : 'ECDHE-ECDSA-AES256-SHA',
        'cipher' : '{ECDHE-ECDSA-AES256-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server2.cert',
        'srv_key' : '/rundir/certs/server2.key',
        'client_ip_prefix' : '16.2',
        'server_ip_prefix' : '106.2'
        },

    {'cipher_name' : 'ECDHE-RSA-AES128-SHA',
        'cipher' : '{ECDHE-RSA-AES128-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '17.2',
        'server_ip_prefix' : '107.2'
        },

    {'cipher_name' : 'ECDHE-RSA-AES256-SHA',
        'cipher' : '{ECDHE-RSA-AES256-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '18.2',
        'server_ip_prefix' : '108.2'
        },

    {'cipher_name' : 'ECDHE-ECDSA-CHACHA20-POLY1305',
        'cipher' : '{ECDHE-ECDSA-CHACHA20-POLY1305}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server2.cert',
        'srv_key' : '/rundir/certs/server2.key',
        'client_ip_prefix' : '19.2',
        'server_ip_prefix' : '109.2'
        },

    {'cipher_name' : 'DHE-RSA-CHACHA20-POLY1305',
        'cipher' : '{DHE-RSA-CHACHA20-POLY1305}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '20.2',
        'server_ip_prefix' : '110.2'
        },	

    {'cipher_name' : 'CAMELLIA128-SHA',
        'cipher' : '{CAMELLIA128-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '21.2',
        'server_ip_prefix' : '111.2'
        },

    {'cipher_name' : 'CAMELLIA256-SHA',
        'cipher' : '{CAMELLIA256-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '22.2',
        'server_ip_prefix' : '112.2'
        },

    {'cipher_name' : 'DHE-RSA-CAMELLIA128-SHA',
        'cipher' : '{DHE-RSA-CAMELLIA128-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '23.2',
        'server_ip_prefix' : '113.2'
        },

    {'cipher_name' : 'DHE-RSA-CAMELLIA256-SHA',
        'cipher' : '{DHE-RSA-CAMELLIA256-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '24.2',
        'server_ip_prefix' : '114.2'
        },

    {'cipher_name' : 'AES128-SHA256',
        'cipher' : '{AES128-SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '25.2',
        'server_ip_prefix' : '115.2'
        },

    {'cipher_name' : 'AES256-SHA256',
        'cipher' : '{AES256-SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '26.2',
        'server_ip_prefix' : '116.2'
        },

    {'cipher_name' : 'DHE-RSA-AES128-SHA256',
        'cipher' : '{DHE-RSA-AES128-SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '27.2',
        'server_ip_prefix' : '117.2'
        },

    {'cipher_name' : 'AES128-GCM-SHA256',
        'cipher' : '{AES128-GCM-SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '28.2',
        'server_ip_prefix' : '118.2'
        },

    {'cipher_name' : 'AES256-GCM-SHA384',
        'cipher' : '{AES256-GCM-SHA384}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '29.2',
        'server_ip_prefix' : '119.2'
        },

    {'cipher_name' : 'ECDHE-RSA-AES128-GCM-SHA256',
        'cipher' : '{ECDHE-RSA-AES128-GCM-SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '30.2',
        'server_ip_prefix' : '120.2'
        },

    {'cipher_name' : 'ECDHE-RSA-AES256-GCM-SHA384',
        'cipher' : '{ECDHE-RSA-AES256-GCM-SHA384}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '31.2',
        'server_ip_prefix' : '121.2'
        },

    {'cipher_name' : 'ECDHE-RSA-AES128-SHA256',
        'cipher' : '{ECDHE-RSA-AES128-SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '32.2',
        'server_ip_prefix' : '122.2'
        },

    {'cipher_name' : 'ECDHE-RSA-AES256-SHA384',
        'cipher' : '{ECDHE-RSA-AES256-SHA384}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '33.2',
        'server_ip_prefix' : '123.2'
        },

    {'cipher_name' : 'DHE-RSA-AES256-SHA256',
        'cipher' : '{DHE-RSA-AES256-SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '34.2',
        'server_ip_prefix' : '124.2'
        },

    {'cipher_name' : 'DHE-RSA-AES256-GCM-SHA384',
        'cipher' : '{DHE-RSA-AES256-GCM-SHA384}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '35.2',
        'server_ip_prefix' : '125.2'
        },

    {'cipher_name' : 'ECDHE-RSA-CHACHA20-POLY1305',
        'cipher' : '{ECDHE-RSA-CHACHA20-POLY1305}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '36.2',
        'server_ip_prefix' : '126.2'
        },

    {'cipher_name' : 'TLS_AES_128_GCM_SHA256',
        'cipher' : '{TLS_AES_128_GCM_SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : 0,
        'tls1_3' : '{tls1_3}',
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '37.2',
        'server_ip_prefix' : '139.2'
        },

    {'cipher_name' : 'TLS_AES_256_GCM_SHA384',
        'cipher' : '{TLS_AES_256_GCM_SHA384}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : 0,
        'tls1_3' : '{tls1_3}',
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '38.2',
        'server_ip_prefix' : '128.2'
        },

    {'cipher_name' : 'TLS_CHACHA20_POLY1305_SHA256',
        'cipher' : '{TLS_CHACHA20_POLY1305_SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : 0,
        'tls1_3' : '{tls1_3}',
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '39.2',
        'server_ip_prefix' : '129.2'
        },

    {'cipher_name' : 'ECDHE-ECDSA-AES128-GCM-SHA256',
        'cipher' : '{ECDHE-ECDSA-AES128-GCM-SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server2.cert',
        'srv_key' : '/rundir/certs/server2.key',
        'client_ip_prefix' : '40.2',
        'server_ip_prefix' : '130.2'
        },

    {'cipher_name' : 'ECDHE-ECDSA-AES256-GCM-SHA384',
        'cipher' : '{ECDHE-ECDSA-AES256-GCM-SHA384}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server2.cert',
        'srv_key' : '/rundir/certs/server2.key',
        'client_ip_prefix' : '41.2',
        'server_ip_prefix' : '131.2'
        },

    {'cipher_name' : 'ECDHE-ECDSA-AES128-SHA256',
        'cipher' : '{ECDHE-ECDSA-AES128-SHA256}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server2.cert',
        'srv_key' : '/rundir/certs/server2.key',
        'client_ip_prefix' : '42.2',
        'server_ip_prefix' : '132.2'
        },

    {'cipher_name' : 'ECDHE-ECDSA-AES256-SHA384',
        'cipher' : '{ECDHE-ECDSA-AES256-SHA384}',
        'sslv3': 0,
        'tls1': 0,
        'tls1_1': 0,
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server2.cert',
        'srv_key' : '/rundir/certs/server2.key',
        'client_ip_prefix' : '43.2',
        'server_ip_prefix' : '133.2'
        },

    {'cipher_name' : 'RC4-MD5',
        'cipher' : '{RC4-MD5}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '44.2',
        'server_ip_prefix' : '134.2'
        },

    {'cipher_name' : 'RC4-SHA',
        'cipher' : '{RC4-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '45.2',
        'server_ip_prefix' : '135.2'
        },

    {'cipher_name' : 'DES-CBC-SHA',
        'cipher' : '{DES-CBC-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '46.2',
        'server_ip_prefix' : '136.2'
        },

    {'cipher_name' : 'DES-CBC3-SHA',
        'cipher' : '{DES-CBC3-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '47.2',
        'server_ip_prefix' : '137.2'
        },

    {'cipher_name' : 'SEED-SHA',
        'cipher' : '{SEED-SHA}',
        'sslv3' : '{sslv3}',
        'tls1' : '{tls1}',
        'tls1_1' : '{tls1_1}',
        'tls1_2' : '{tls1_2}',
        'tls1_3' : 0,
        'srv_cert' : '/rundir/certs/server.cert',
        'srv_key' : '/rundir/certs/server.key',
        'client_ip_prefix' : '48.2',
        'server_ip_prefix' : '138.2'}
]


def start_containers(host_info, c_args):
    rundir_map = "--volume={}:{}".format (c_args.host_rundir
                                                , c_args.target_rundir)

    srcdir_map = "--volume={}:{}".format (c_args.host_srcdir
                                                , c_args.target_srcdir)

    for z_index in range(host_info['cores']):
        zone_cname = "tp-zone-{}".format (z_index+1)

        cmd_str = "sudo docker run --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --network=bridge --privileged --name {} -it -d {} {} tlspack/tgen:latest /bin/bash".format (zone_cname, rundir_map, srcdir_map)
        os.system (cmd_str)

        for netdev in host_info['net_dev_list']:
            cmd_str = "sudo ip link set dev {} up".format(netdev)
            os.system (cmd_str)
            cmd_str = "sudo docker network connect {} {}".format(host_info['net_macvlan_map'][netdev], zone_cname)
            os.system (cmd_str)

def stop_containers(host_info, c_args):
    for z_index in range(host_info['cores']):
        zone_cname = "tp-zone-{}".format (z_index+1)
        cmd_str = "sudo docker rm -f {}".format (zone_cname)
        os.system (cmd_str)

def restart_containers(host_info, c_args):
    stop_containers(host_info, c_args)
    start_containers(host_info, c_args)


def add_common_params (arg_parser):
    arg_parser.add_argument('--sysinit'
                                , action="store_true"
                                , default=False
                                , help = 'sysinit')

    arg_parser.add_argument('--host_rundir'
                                , action="store"
                                , default='/root/rundir'
                                , help = 'rundir path')

    arg_parser.add_argument('--target_rundir'
                                , action="store"
                                , default='/rundir'
                                , help = 'rundir path in container')

    arg_parser.add_argument('--host_srcdir'
                                , action="store"
                                , default='/root/tcpdash'
                                , help = 'host_srcdir')

    arg_parser.add_argument('--target_srcdir'
                                , action="store"
                                , default='/root/tcpdash'
                                , help = 'target_srcdir')


def add_common_start_params(arg_parser):

    arg_parser.add_argument('--runtag'
                                , action="store"
                                , required=True
                                , help = 'run id')

def add_traffic_params (arg_parser):

    add_common_params (arg_parser)

    add_common_start_params (arg_parser)

    arg_parser.add_argument('--na'
                                , action="store"
                                , required=True
                                , dest='na_iface'
                                , help = 'na_iface name')

    arg_parser.add_argument('--nb'
                                , action="store"
                                , required=True
                                , dest='nb_iface'
                                , help = 'nb_iface name')

    arg_parser.add_argument('--zones'
                                , action="store"
                                , type=int
                                , default=1
                                , help = 'zones ')

    arg_parser.add_argument('--cps'
                                , action="store"
                                , type=int
                                , required=True
                                , help = 'tps : 1 - 10000')

    arg_parser.add_argument('--max_pipeline'
                                , action="store"
                                , type=int
                                , default=100
                                , help = 'max_pipeline : 1 - 10000')

    arg_parser.add_argument('--max_active'
                                , action="store"
                                , type=int
                                , default=100
                                , help = 'max_active : 1 - 2000000')

    arg_parser.add_argument('--cipher'
                                , action="store"
                                , help = 'command name'
                                , required=True)

    arg_parser.add_argument('--sslv3'
                                , action="store_true"
                                , default=False
                                , help = '0/1')

    arg_parser.add_argument('--tls1'
                                , action="store_true"
                                , default=False
                                , help = '0/1')
                                
    arg_parser.add_argument('--tls1_1'
                                , action="store_true"
                                , default=False
                                , help = '0/1')

    arg_parser.add_argument('--tls1_2'
                                , action="store_true"
                                , default=False
                                , help = '0/1')

    arg_parser.add_argument('--tls1_3'
                                , action="store_true"
                                , default=False
                                , help = '0/1')

    arg_parser.add_argument('--tcpdump'
                                , action="store"
                                , help = 'tcpdump options'
                                , default='-c 1000')

    arg_parser.add_argument('--total_conn_count'
                                , action="store"
                                , type=int
                                , default=0
                                , help = 'total connection counts')

    arg_parser.add_argument('--client_mac_seed'
                                , action="store"
                                , help = '5 bytes'
                                , default='02:42:ac:14:00')

    arg_parser.add_argument('--server_mac_seed'
                                , action="store"
                                , help = '5 bytes'
                                , default='02:42:ac:15:00')

    arg_parser.add_argument('--app_next_write'
                                , action="store"
                                , type=int
                                , default=0
                                , help = 'app_next_write')

    arg_parser.add_argument('--app_cs_data_len'
                                , action="store"
                                , type=int
                                , default=128
                                , help = 'app_cs_data_len')

    arg_parser.add_argument('--app_sc_data_len'
                                , action="store"
                                , type=int
                                , default=128
                                , help = 'app_sc_data_len')

    arg_parser.add_argument('--app_rcv_buff'
                                , action="store"
                                , type=int
                                , default=0
                                , help = 'app_rcv_buff')

    arg_parser.add_argument('--app_snd_buff'
                                , action="store"
                                , type=int
                                , default=0
                                , help = 'app_snd_buff')

    arg_parser.add_argument('--tcp_rcv_buff'
                                , action="store"
                                , type=int
                                , default=0
                                , help = 'tcp_rcv_buff')

    arg_parser.add_argument('--tcp_snd_buff'
                                , action="store"
                                , type=int
                                , default=0
                                , help = 'tcp_snd_buff')

    arg_parser.add_argument('--app_cs_starttls_len'
                                , action="store"
                                , type=int
                                , default=0
                                , help = 'app_cs_starttls_len')

    arg_parser.add_argument('--app_sc_starttls_len'
                            , action="store"
                            , type=int
                            , default=0
                            , help = 'app_sc_starttls_len')



def add_proxy_params (arg_parser):

    add_common_params (arg_parser)

    add_common_start_params (arg_parser)

    arg_parser.add_argument('--proxy_traffic_vlan'
                                , action="store"
                                , type=int
                                , required=True
                                , help = '1-4095')

    arg_parser.add_argument('--ta'
                                , action="store"
                                , required=True
                                , dest = 'ta_iface'
                                , help = 'ta host interface')

    arg_parser.add_argument('--tb'
                                , action="store"
                                , required=True
                                , dest = 'tb_iface'
                                , help = 'tb host interface')

    arg_parser.add_argument('--ta_macvlan'
                                , action="store"
                                , default=''
                                , help = 'ta host macvlan')

    arg_parser.add_argument('--tb_macvlan'
                                , action="store"
                                , default=''
                                , help = 'tb host macvlan')

    arg_parser.add_argument('--ta_iface_container'
                                , action="store"
                                , help = 'ta interface'
                                , default='eth1')

    arg_parser.add_argument('--tb_iface_container'
                                , action="store"
                                , help = 'tb interface'
                                , default='eth2')

    arg_parser.add_argument('--ta_subnet'
                                , action="store"
                                , help = 'ta subnet'
                                , required=True)

    arg_parser.add_argument('--tb_subnet'
                                , action="store"
                                , help = 'tb subnet'
                                , required=True)

    arg_parser.add_argument('--ta_tcpdump'
                                , action="store"
                                , help = 'ta tcpdump'
                                , default='-c 100')

    arg_parser.add_argument('--tb_tcpdump'
                                , action="store"
                                , help = 'tb tcpdump'
                                , default='-c 100')

    arg_parser.add_argument('--client_mac_seed'
                                , action="store"
                                , help = '5 bytes'
                                , default='02:42:ac:14:00')

    arg_parser.add_argument('--server_mac_seed'
                                , action="store"
                                , help = '5 bytes'
                                , default='02:42:ac:15:00')

def add_stop_params (arg_parser):
    add_common_params (arg_parser)

def add_status_params(arg_parser):
    add_common_params (arg_parser)

def zone_start_thread(host_info, c_args, zone, z_index):

    zone_cname = "tp-zone-{}".format (z_index+1)
    cmd_str = "sudo docker exec -d {} ip netns add {}".format(zone_cname, host_info['netns'])
    os.system (cmd_str)

    for netdev in host_info['net_iface_map'].values():
        cmd_str = "sudo docker exec -d {} ip link set dev {} netns {}".format(zone_cname,
                                                                netdev,
                                                                host_info['netns'])
        os.system (cmd_str)

    cmd_str = "sudo docker exec -d {} cp -f /rundir/bin/tlspack.exe /usr/local/bin".format(zone_cname)
    os.system (cmd_str)

    cmd_str = "sudo docker exec -d {} chmod +x /usr/local/bin/tlspack.exe".format(zone_cname)
    os.system (cmd_str)

    cmd_str = "sudo docker exec -d {} cp -f /rundir/bin/tlspack.py /usr/local/bin".format(zone_cname)
    os.system (cmd_str)

    cmd_str = "sudo docker exec -d {} chmod +x /usr/local/bin/tlspack.py".format(zone_cname)
    os.system (cmd_str)


    cfg_file = os.path.join(c_args.target_rundir, 'traffic', c_args.runtag, 'config.json')
    cmd_ctrl_dir = os.path.join(c_args.target_rundir, 'traffic', c_args.runtag, 'cmdctl', zone['zone_label'])
    result_dir = os.path.join(c_args.target_rundir, 'traffic', c_args.runtag, 'result', zone['zone_label'])
    started_file = os.path.join (cmd_ctrl_dir, 'started.txt')

    start_cmd_internal = '"ip netns exec {} /usr/local/bin/tlspack.exe {} {} {} {}"'.format (host_info['netns']
                                                                                        , result_dir.rstrip('/')
                                                                                        , started_file
                                                                                        , cfg_file
                                                                                        , z_index)
    stop_cmd_internal = ''
    for netdev in host_info['net_iface_map'].values():
        cmd = ' "ip netns exec {} ip link set {} netns 1"'.format (host_info['netns'], netdev)
        stop_cmd_internal += cmd
    stop_cmd_internal += ' "ip netns del {}"'.format(host_info['netns'])

    cmd_str = 'sudo docker exec -d {} python3 /usr/local/bin/tlspack.py {} {} {}'.format (zone_cname,
                                                                        cmd_ctrl_dir,
                                                                        start_cmd_internal, 
                                                                        stop_cmd_internal)
    os.system (cmd_str)


    cmd_ctrl_dir = os.path.join(c_args.host_rundir, 'traffic', c_args.runtag, 'cmdctl', zone['zone_label'])
    started_file = os.path.join(cmd_ctrl_dir, 'started.txt')
    finish_file = os.path.join (cmd_ctrl_dir, 'finish.txt')
    while True:
        time.sleep (1)
        if os.path.exists (started_file) or os.path.exists (finish_file):
            break

def start_traffic(host_info, c_args, traffic_s):
    registry_dir = os.path.join(c_args.host_rundir, 'registry', 'one-app-mode')
    registry_file = os.path.join(registry_dir, 'tag.txt')

    if c_args.sysinit:
        restart_containers (host_info, c_args)
        os.system ("rm -rf {}".format (registry_dir))

    # check if config runing
    if os.path.exists(registry_file):
        with open (registry_file) as f:
            testname = f.read()

        if testname == c_args.runtag:
            print 'error: {} already running'.format (testname)
        else:
            print 'error: {} running'.format (testname)
        sys.exit(1)

    # create config dir; file
    try:
        cfg_j = json.loads (traffic_s)
        traffic_s = json.dumps(cfg_j, indent=4)
    except:
        print traffic_s
        sys.exit(1)

    cfg_dir = os.path.join(c_args.host_rundir, 'traffic', c_args.runtag)
    cfg_file = os.path.join(cfg_dir, 'config.json')

    os.system ( 'rm -rf {}'.format(cfg_dir) )
    os.system ( 'mkdir -p {}'.format(cfg_dir) )

    with open(cfg_file, 'w') as f:
        f.write(traffic_s)

    # create registry entries
    os.system ('mkdir -p {}'.format(registry_dir))

    with open(registry_file, 'w') as f:
        f.write(c_args.runtag)

    for zone in cfg_j['zones']:
        if not zone['enable']:
            continue
        is_app_enable = False
        for app in zone['app_list']:
            if app['enable']:
                is_app_enable = True;
                break
        if not is_app_enable:
            continue
    
        zone_file = os.path.join(registry_dir, zone['zone_label'])  
        with open(zone_file, 'w') as f:
            f.write('0')
    
    master_file = os.path.join(registry_dir, 'master')
    with open(master_file, 'w') as f:
        f.write('0')  

    # create cmd_ctrl entries
    cmd_ctrl_dir = os.path.join(cfg_dir, 'cmdctl')
    os.system ('rm -rf {}'.format(cmd_ctrl_dir))
    os.system ('mkdir -p {}'.format(cmd_ctrl_dir))
    for zone in cfg_j['zones']:
        if not zone['enable']:
            continue
        zone_dir = os.path.join (cmd_ctrl_dir, zone['zone_label'])
        os.system ('mkdir -p {}'.format(zone_dir))


    # create resullt entries
    result_dir = os.path.join(c_args.host_rundir, 'traffic', c_args.runtag, 'result')
    os.system ('rm -rf {}'.format(result_dir))
    os.system ('mkdir -p {}'.format(result_dir))

    zone_map = {}
    for zone in cfg_j['zones']:
        if not zone['enable']:
            continue

        zone_map[zone['zone_label']] = False

        zone_dir = os.path.join (result_dir, zone['zone_label'])
        os.system ('mkdir -p {}'.format(zone_dir))

        for app in zone['app_list']:
            if not app['enable']:
                continue
            app_dir = os.path.join (zone_dir, app['app_label'])
            os.system ('mkdir -p {}'.format(app_dir))

            if app.get('srv_list'):
                for srv in app['srv_list']:
                    if not srv['enable']:
                        continue
                    srv_dir = os.path.join (app_dir, srv['srv_label'])
                    os.system ('mkdir -p {}'.format(srv_dir))

            if app.get('proxy_list'):
                for proxy in app['proxy_list']:
                    if not proxy['enable']:
                        continue
                    proxy_dir = os.path.join (app_dir, proxy['proxy_label'])
                    os.system ('mkdir -p {}'.format(proxy_dir))

            if app.get('cs_grp_list'):
                for cs_grp in app['cs_grp_list']:
                    if not cs_grp['enable']:
                        continue
                    cs_grp_dir = os.path.join (app_dir, cs_grp['cs_grp_label'])
                    os.system ('mkdir -p {}'.format(cs_grp_dir))

    # start zones
    for netdev in host_info['net_dev_list']:
        cmd_str = "sudo ip link set dev {} up".format(netdev)
        os.system (cmd_str)

    next_step = 0
    while next_step < host_info['max_sequence']:
        next_step += 1
        z_threads = []
        z_index = -1
        for zone in cfg_j['zones']:
            z_index += 1

            if not zone['enable']:
                continue

            if zone.get('step', 1) == next_step:
                # zone_start_thread (host_info, c_args, zone, z_index)
                thd = Thread(target=zone_start_thread, args=[host_info, c_args, zone, z_index])
                thd.daemon = True
                thd.start()
                z_threads.append(thd)
        if z_threads:
            for thd in z_threads:
                thd.join()
            time.sleep(1) #can be removed later

    return (cfg_dir, result_dir)

def zone_stop_thread(host_info, c_args, zone, z_index):

    cmd_ctrl_dir = os.path.join(c_args.host_rundir, 'traffic', c_args.runtag, 'cmdctl', zone['zone_label'])

    stop_file = os.path.join(cmd_ctrl_dir, 'stop.txt')
    while True:
        time.sleep(1)
        if os.path.exists (stop_file):
            break
        try:
            with open (stop_file, 'w') as f:
                f.write('1')
        except:
            pass

    finish_file = os.path.join(cmd_ctrl_dir, 'finish.txt')
    while True:
        time.sleep (1)
        if os.path.exists (finish_file):
            break

def stop_traffic(host_info, c_args):
    registry_dir = os.path.join(c_args.host_rundir, 'registry', 'one-app-mode')
    registry_file = os.path.join(registry_dir, 'tag.txt')

    if c_args.sysinit:
        restart_containers (host_info, c_args)
        os.system ("rm -rf {}".format (registry_dir))
        return

    # check if config runing
    if not os.path.exists(registry_file):
        print 'no test running'
        sys.exit(1)    

    with open (registry_file) as f:
        c_args.runtag = f.read()

    cfg_dir = os.path.join(c_args.host_rundir, 'traffic', c_args.runtag)
    cfg_file = os.path.join(cfg_dir, 'config.json')

    try:
        with open(cfg_file) as f:
            cfg_j = json.load(f)
    except:
        print 'invalid config file' 
        sys.exit(1)


    z_threads = []
    z_index = -1
    for zone in cfg_j['zones']:
        z_index += 1

        if not zone['enable']:
            continue

        thd = Thread(target=zone_stop_thread, args=[host_info, c_args, zone, z_index])
        thd.daemon = True
        thd.start()
        z_threads.append(thd)

    for thd in z_threads:
        thd.join()

    os.system ("rm -rf {}".format (registry_dir))

def show_traffic (host_info, c_args):
    registry_dir = os.path.join(c_args.host_rundir, 'registry', 'one-app-mode')
    registry_file = os.path.join(registry_dir, 'tag.txt')

    # check if config runing
    if os.path.exists(registry_file):
        with open (registry_file) as f:
            testname = f.read()
        print '{} running'.format (testname)
    else:
        print 'no test running'

def is_traffic (c_args):
    registry_dir = os.path.join(c_args.host_rundir, 'registry', 'one-app-mode')
    registry_file = os.path.join(registry_dir, 'tag.txt')
    if os.path.exists(registry_file):
        return True     
    return False



def add_cps_params (cmd_parser):
    cmd_parser.add_argument('--ecdsa_cert'
                                , action="store_true"
                                , default=False
                                , help = '0/1')

def process_cps_template (cmd_args):
    tlspack_cfg = jinja2.Template('''
    {
        "tgen_app" : "cps",
        "zones" : [
            {% set ns = namespace(cs_grp_count=0, srv_count=0) %}
            {%- for zone_id in range(1, PARAMS.zones+1) %}
                {
                    "zone_label" : "zone-{{zone_id}}-client",
                    "enable" : 1,
                    "step" : 2,
                    "app_list" : [
                        {
                            "app_type" : "tls_client",
                            "app_label" : "tls_client_1",
                            "enable" : 1,
                            "conn_per_sec" : {{PARAMS.cps}},
                            "max_pending_conn_count" : {{PARAMS.max_pipeline}},
                            "max_active_conn_count" : {{PARAMS.max_active}},
                            "total_conn_count" : {{PARAMS.total_conn_count}},
                            "cs_grp_list" : [
                                {% set ns.cs_grp_count = 0 %}
                                {%- for tls_ver in ['sslv3', 'tls1', 'tls1_1', 'tls1_2', 'tls1_3'] %}
                                    {%- if (tls_ver == 'sslv3' and PARAMS.sslv3) 
                                            or (tls_ver == 'tls1' and PARAMS.tls1) 
                                            or (tls_ver == 'tls1_1' and PARAMS.tls1_1) 
                                            or (tls_ver == 'tls1_2' and PARAMS.tls1_2) 
                                            or (tls_ver == 'tls1_3' and PARAMS.tls1_3) %}
                                        {{ "," if ns.cs_grp_count }}
                                        {% set ns.cs_grp_count = ns.cs_grp_count+1 %}
                                        {
                                            "cs_grp_label" : "cs_grp_{{loop.index}}",
                                            "enable" : 1,
                                            "srv_ip"   : "14.2{{zone_id}}.51.{{loop.index}}",
                                            "srv_port" : 443,
                                            "clnt_ip_begin" : "12.2{{zone_id}}.51.{{1+loop.index0*10}}",
                                            "clnt_ip_end" : "12.2{{zone_id}}.51.{{loop.index*10}}",
                                            "clnt_port_begin" : 5000,
                                            "clnt_port_end" : 65000,
                                            "cipher" : "{{PARAMS.cipher}}",
                                            "tls_version" : "{{tls_ver}}",
                                            "close_type" : "fin",
                                            "close_notify" : "no_send",
                                            "app_rcv_buff" : {{PARAMS.app_rcv_buff}},
                                            "app_snd_buff" : {{PARAMS.app_snd_buff}},
                                            "write_chunk" : {{PARAMS.app_next_write}},
                                            "tcp_rcv_buff" : {{PARAMS.tcp_rcv_buff}},
                                            "tcp_snd_buff" : {{PARAMS.tcp_snd_buff}},
                                            "cs_data_len" : {{PARAMS.app_cs_data_len}},
                                            "sc_data_len" : {{PARAMS.app_sc_data_len}},
                                            "cs_start_tls_len" : {{PARAMS.app_cs_starttls_len}},
                                            "sc_start_tls_len" : {{PARAMS.app_sc_starttls_len}}
                                        }
                                    {%- endif %}
                                {%- endfor %}                         
                            ]
                        }
                    ],

                    "zone_cmds" : [
                        "ip link set dev {{PARAMS.na_iface_container}} up",
                        "ifconfig {{PARAMS.na_iface_container}} hw ether {{PARAMS.client_mac_seed}}:{{'{:02x}'.format(zone_id)}}",
                        "ip route add default dev {{PARAMS.na_iface_container}} table 200",
                        "ip -4 route add local 12.2{{zone_id}}.51.0/24 dev lo",
                        "ip rule add from 12.2{{zone_id}}.51.0/24 table 200",
                        "tcpdump -i {{PARAMS.na_iface_container}} {{PARAMS.tcpdump}} -w {{PARAMS.result_dir_container}}/zone-{{zone_id}}-client/init.pcap &"
                    ]
                }
                ,
                {
                    "zone_label" : "zone-{{zone_id}}-server",
                    "enable" : 1,
                    "step" : 1,
                    "app_list" : [
                        {
                            "app_type" : "tls_server",
                            "app_label" : "tls_server_1",
                            "enable" : 1,
                            "srv_list" : [
                                {% set ns.srv_count = 0 %}
                                {%- for tls_ver in ['sslv3', 'tls1', 'tls1_1', 'tls1_2', 'tls1_3'] %}
                                    {%- if (tls_ver == 'sslv3' and PARAMS.sslv3) 
                                            or (tls_ver == 'tls1' and PARAMS.tls1) 
                                            or (tls_ver == 'tls1_1' and PARAMS.tls1_1) 
                                            or (tls_ver == 'tls1_2' and PARAMS.tls1_2) 
                                            or (tls_ver == 'tls1_3' and PARAMS.tls1_3) %}
                                        {{ "," if ns.srv_count }}
                                        {% set ns.srv_count = ns.srv_count+1 %}
                                        {
                                            "srv_label" : "srv_{{loop.index}}",
                                            "enable" : 1,
                                            "emulation_id" : 0,
                                            "begin_cert_index" : {{zone_id*2000}},
                                            "end_cert_index" : 100000, 
                                            "srv_ip" : "14.2{{zone_id}}.51.{{loop.index}}",
                                            "srv_port" : 443,
                                            "srv_cert" : "{{PARAMS.server_cert}}",
                                            "srv_key" : "{{PARAMS.server_key}}",
                                            "cipher" : "{{PARAMS.cipher}}",
                                            "tls_version" : "{{tls_ver}}",
                                            "close_type" : "fin",
                                            "close_notify" : "no_send",
                                            "app_rcv_buff" : {{PARAMS.app_rcv_buff}},
                                            "app_snd_buff" : {{PARAMS.app_snd_buff}},
                                            "write_chunk" : {{PARAMS.app_next_write}},
                                            "tcp_rcv_buff" : {{PARAMS.tcp_rcv_buff}},
                                            "tcp_snd_buff" : {{PARAMS.tcp_snd_buff}},
                                            "cs_data_len" : {{PARAMS.app_cs_data_len}},
                                            "sc_data_len" : {{PARAMS.app_sc_data_len}},
                                            "cs_start_tls_len" : {{PARAMS.app_cs_starttls_len}},
                                            "sc_start_tls_len" : {{PARAMS.app_sc_starttls_len}}
                                        }
                                    {%- endif %}
                                {%- endfor %}
                            ]
                        }
                    ],

                    "zone_cmds" : [
                        "ip link set dev {{PARAMS.nb_iface_container}} up",
                        "ifconfig {{PARAMS.nb_iface_container}} hw ether {{PARAMS.server_mac_seed}}:{{'{:02x}'.format(zone_id)}}",
                        "ip route add default dev {{PARAMS.nb_iface_container}} table 200",
                        "ip -4 route add local 14.2{{zone_id}}.51.0/24 dev lo",
                        "ip rule add from 14.2{{zone_id}}.51.0/24 table 200",
                        "tcpdump -i {{PARAMS.nb_iface_container}} {{PARAMS.tcpdump}} -w {{PARAMS.result_dir_container}}/zone-{{zone_id}}-server/init.pcap &"
                    ]
                }
                {{ "," if not loop.last }}
            {%- endfor %}
        ]
    }
    ''')
    if cmd_args.ecdsa_cert:
        cmd_args.server_cert = '/rundir/certs/server2.cert'
        cmd_args.server_key = '/rundir/certs/server2.key'
    else:
        cmd_args.server_cert = '/rundir/certs/server.cert'
        cmd_args.server_key = '/rundir/certs/server.key'
    return tlspack_cfg.render(PARAMS = cmd_args)

def process_cps_stats(result_dir):
    ev_sockstats_client_list = []
    ev_sockstats_server_list = []

    result_dir_contents = []
    try:
        result_dir_contents = os.listdir(result_dir)
    except:
        pass

    for zone_dir in result_dir_contents:
        zone_dir_path = os.path.join(result_dir, zone_dir)
        if os.path.isdir(zone_dir_path):
            ev_sockstats_json_file = os.path.join (zone_dir_path
                                            , 'ev_sockstats.json')
            try:
                with open(ev_sockstats_json_file) as f:
                    stats_j = json.load(f)
                    if zone_dir.endswith('-client'):
                        ev_sockstats_client_list.append (stats_j)
                    if zone_dir.endswith('-server'):
                        ev_sockstats_server_list.append (stats_j)
            except:
                pass

    if ev_sockstats_client_list:
        ev_sockstats = ev_sockstats_client_list.pop()
        while ev_sockstats_client_list:
            next_ev_sockstats = ev_sockstats_client_list.pop()
            for k, v in next_ev_sockstats.items():
                ev_sockstats[k] += v
        with open(os.path.join(result_dir, 'ev_sockstats_client.json'), 'w') as f:
            json.dump(ev_sockstats, f)

    if ev_sockstats_server_list:
        ev_sockstats = ev_sockstats_server_list.pop()
        while ev_sockstats_server_list:
            next_ev_sockstats = ev_sockstats_server_list.pop()
            for k, v in next_ev_sockstats.items():
                ev_sockstats[k] += v
        with open(os.path.join(result_dir, 'ev_sockstats_server.json'), 'w') as f:
            json.dump(ev_sockstats, f)



def add_bw_params (cmd_parser):
    cmd_parser.add_argument('--ecdsa_cert'
                                , action="store_true"
                                , default=False
                                , help = '0/1')

def process_bw_template (cmd_args):

    tlspack_cfg = jinja2.Template('''
    {
        "tgen_app" : "bw",
        "zones" : [
            {% set ns = namespace(cs_grp_count=0, srv_count=0) %}
            {%- for zone_id in range(1, PARAMS.zones+1) %}
                {
                    "zone_label" : "zone-{{zone_id}}-client",
                    "enable" : 1,

                    "app_list" : [
                        {
                            "app_type" : "tls_client",
                            "app_label" : "tls_client_1",
                            "enable" : 1,
                            "conn_per_sec" : {{PARAMS.cps}},
                            "max_pending_conn_count" : {{PARAMS.max_pipeline}},
                            "max_active_conn_count" : {{PARAMS.max_active}},
                            "total_conn_count" : {{PARAMS.total_conn_count}},
                            "cs_grp_list" : [
                                {% set ns.cs_grp_count = 0 %}
                                {%- for tls_ver in ['sslv3', 'tls1', 'tls1_1', 'tls1_2', 'tls1_3'] %}
                                    {%- if (tls_ver == 'sslv3' and PARAMS.sslv3) 
                                            or (tls_ver == 'tls1' and PARAMS.tls1) 
                                            or (tls_ver == 'tls1_1' and PARAMS.tls1_1) 
                                            or (tls_ver == 'tls1_2' and PARAMS.tls1_2) 
                                            or (tls_ver == 'tls1_3' and PARAMS.tls1_3) %}
                                        {{ "," if ns.cs_grp_count }}
                                        {% set ns.cs_grp_count = ns.cs_grp_count+1 %}
                                        {
                                            "cs_grp_label" : "cs_grp_{{loop.index}}",
                                            "enable" : 1,
                                            "srv_ip"   : "24.2{{zone_id}}.51.{{loop.index}}",
                                            "srv_port" : 443,
                                            "clnt_ip_begin" : "22.2{{zone_id}}.51.{{1+loop.index0*10}}",
                                            "clnt_ip_end" : "22.2{{zone_id}}.51.{{loop.index*10}}",
                                            "clnt_port_begin" : 5000,
                                            "clnt_port_end" : 65000,
                                            "cipher" : "{{PARAMS.cipher}}",
                                            "tls_version" : "{{tls_ver}}",
                                            "close_type" : "reset",
                                            "close_notify" : "no_send",
                                            "app_rcv_buff" : {{PARAMS.app_rcv_buff}},
                                            "app_snd_buff" : {{PARAMS.app_snd_buff}},
                                            "write_chunk" : {{PARAMS.app_next_write}},
                                            "tcp_rcv_buff" : {{PARAMS.tcp_rcv_buff}},
                                            "tcp_snd_buff" : {{PARAMS.tcp_snd_buff}},
                                            "cs_data_len" : {{PARAMS.app_cs_data_len}},
                                            "sc_data_len" : {{PARAMS.app_sc_data_len}},
                                            "cs_start_tls_len" : {{PARAMS.app_cs_starttls_len}},
                                            "sc_start_tls_len" : {{PARAMS.app_sc_starttls_len}}
                                        }
                                    {%- endif %}
                                {%- endfor %}                         
                            ]
                        }
                    ],

                    "zone_cmds" : [
                        "ip link set dev {{PARAMS.na_iface_container}} up",
                        "ifconfig {{PARAMS.na_iface_container}} hw ether {{PARAMS.client_mac_seed}}:{{'{:02x}'.format(zone_id)}}",
                        "ip route add default dev {{PARAMS.na_iface_container}} table 200",
                        "ip -4 route add local 22.2{{zone_id}}.51.0/24 dev lo",
                        "ip rule add from 22.2{{zone_id}}.51.0/24 table 200",
                        "tcpdump -i {{PARAMS.na_iface_container}} {{PARAMS.tcpdump}} -w {{PARAMS.result_dir_container}}/zone-{{zone_id}}-client/init.pcap &"
                    ]                    
                }
                ,
                {
                    "zone_label" : "zone-{{zone_id}}-server",
                    "enable" : 1,

                    "app_list" : [
                        {
                            "app_type" : "tls_server",
                            "app_label" : "tls_server_1",
                            "enable" : 1,
                            "srv_list" : [
                                {% set ns.srv_count = 0 %}
                                {%- for tls_ver in ['sslv3', 'tls1', 'tls1_1', 'tls1_2', 'tls1_3'] %}
                                    {%- if (tls_ver == 'sslv3' and PARAMS.sslv3) 
                                            or (tls_ver == 'tls1' and PARAMS.tls1) 
                                            or (tls_ver == 'tls1_1' and PARAMS.tls1_1) 
                                            or (tls_ver == 'tls1_2' and PARAMS.tls1_2) 
                                            or (tls_ver == 'tls1_3' and PARAMS.tls1_3) %}
                                        {{ "," if ns.srv_count }}
                                        {% set ns.srv_count = ns.srv_count+1 %}
                                        {
                                            "srv_label" : "srv_{{loop.index}}",
                                            "enable" : 1,
                                            "srv_ip" : "24.2{{zone_id}}.51.{{loop.index}}",
                                            "srv_port" : 443,
                                            "srv_cert" : "{{PARAMS.server_cert}}",
                                            "srv_key" : "{{PARAMS.server_key}}",
                                            "cipher" : "{{PARAMS.cipher}}",
                                            "tls_version" : "{{tls_ver}}",
                                            "close_type" : "reset",
                                            "close_notify" : "no_send",
                                            "app_rcv_buff" : {{PARAMS.app_rcv_buff}},
                                            "app_snd_buff" : {{PARAMS.app_snd_buff}},
                                            "write_chunk" : {{PARAMS.app_next_write}},
                                            "tcp_rcv_buff" : {{PARAMS.tcp_rcv_buff}},
                                            "tcp_snd_buff" : {{PARAMS.tcp_snd_buff}},
                                            "cs_data_len" : {{PARAMS.app_cs_data_len}},
                                            "sc_data_len" : {{PARAMS.app_sc_data_len}},
                                            "cs_start_tls_len" : {{PARAMS.app_cs_starttls_len}},
                                            "sc_start_tls_len" : {{PARAMS.app_sc_starttls_len}}
                                        }
                                    {%- endif %}
                                {%- endfor %}
                            ]
                        }
                    ],

                    "zone_cmds" : [
                        "ip link set dev {{PARAMS.nb_iface_container}} up",
                        "ifconfig {{PARAMS.nb_iface_container}} hw ether {{PARAMS.server_mac_seed}}:{{'{:02x}'.format(zone_id)}}",
                        "ip route add default dev {{PARAMS.nb_iface_container}} table 200",
                        "ip -4 route add local 24.2{{zone_id}}.51.0/24 dev lo",
                        "ip rule add from 24.2{{zone_id}}.51.0/24 table 200",
                        "tcpdump -i {{PARAMS.nb_iface_container}} {{PARAMS.tcpdump}} -w {{PARAMS.result_dir_container}}/zone-{{zone_id}}-server/init.pcap &"
                    ]
                }
                {{ "," if not loop.last }}
            {%- endfor %}
        ]
    }
    ''')

    if cmd_args.ecdsa_cert:
        cmd_args.server_cert = '/rundir/certs/server2.cert'
        cmd_args.server_key = '/rundir/certs/server2.key'
    else:
        cmd_args.server_cert = '/rundir/certs/server.cert'
        cmd_args.server_key = '/rundir/certs/server.key'
    return tlspack_cfg.render(PARAMS = cmd_args)

def process_bw_stats(result_dir):
    ev_sockstats_client_list = []
    ev_sockstats_server_list = []

    result_dir_contents = []
    try:
        result_dir_contents = os.listdir(result_dir)
    except:
        pass

    for zone_dir in result_dir_contents:
        zone_dir_path = os.path.join(result_dir, zone_dir)
        if os.path.isdir(zone_dir_path):
            ev_sockstats_json_file = os.path.join (zone_dir_path
                                            , 'ev_sockstats.json')
            try:
                with open(ev_sockstats_json_file) as f:
                    stats_j = json.load(f)
                    if zone_dir.endswith('-client'):
                        ev_sockstats_client_list.append (stats_j)
                    if zone_dir.endswith('-server'):
                        ev_sockstats_server_list.append (stats_j)
            except:
                ev_sockstats_client_list = []
                ev_sockstats_server_list = []
                break
    if ev_sockstats_client_list:
        ev_sockstats = ev_sockstats_client_list.pop()
        while ev_sockstats_client_list:
            next_ev_sockstats = ev_sockstats_client_list.pop()
            for k, v in next_ev_sockstats.items():
                ev_sockstats[k] += v
        with open(os.path.join(result_dir, 'ev_sockstats_client.json'), 'w') as f:
            json.dump(ev_sockstats, f)

    if ev_sockstats_server_list:
        ev_sockstats = ev_sockstats_server_list.pop()
        while ev_sockstats_server_list:
            next_ev_sockstats = ev_sockstats_server_list.pop()
            for k, v in next_ev_sockstats.items():
                ev_sockstats[k] += v
        with open(os.path.join(result_dir, 'ev_sockstats_server.json'), 'w') as f:
            json.dump(ev_sockstats, f)


def add_tproxy_params (cmd_parser):
    pass

def process_tproxy_template (cmd_args):
    tlspack_cfg = jinja2.Template ('''{
        "tgen_app" : "tproxy",
        "zones" : [
            {
                "zone_label" : "zone-1-proxy",
                "enable" : 1,
            
                "app_list" : [
                    {
                        "app_type" : "tcp_proxy",
                        "app_label" : "tcp_proxy_1",
                        "enable" : 1,

                        "proxy_list" : [
                            {
                                "proxy_label" : "bae-issue",
                                "enable" : 1,

                                "proxy_ip" : "0.0.0.0",
                                "proxy_port" : 883,
                                "proxy_type_id" : 1,

                                "tcp_rcv_buff" : 0,
                                "tcp_snd_buff" : 0
                            }
                        ]
                    }
                ],
                
                "host_cmds" : [
                    "sudo ip link set dev {{PARAMS.ta_iface}} up",
                    "sudo ip link set dev {{PARAMS.tb_iface}} up",
                    "sudo docker network connect {{PARAMS.ta_macvlan}} {{PARAMS.runtag}}-zone-1-proxy",
                    "sudo docker network connect {{PARAMS.tb_macvlan}} {{PARAMS.runtag}}-zone-1-proxy"
                ],

                "zone_cmds" : [
                    "sysctl net.ipv4.conf.all.rp_filter=0",
                    "sysctl net.ipv4.conf.default.rp_filter=0",

                    "ip link set dev {{PARAMS.ta_iface_container}} up",
                    "ifconfig {{PARAMS.ta_iface_container}} hw ether 00:50:56:8c:5a:54",
                    "sysctl net.ipv4.conf.{{PARAMS.ta_iface_container}}.rp_filter=0",
                    "ip link add link {{PARAMS.ta_iface_container}} name {{PARAMS.ta_iface_container}}.{{PARAMS.proxy_traffic_vlan}} type vlan id {{PARAMS.proxy_traffic_vlan}}",
                    "ip link set dev {{PARAMS.ta_iface_container}}.{{PARAMS.proxy_traffic_vlan}} up",
                    "ip addr add 1.1.1.1/24 dev {{PARAMS.ta_iface_container}}.{{PARAMS.proxy_traffic_vlan}}",
                    "arp -i {{PARAMS.ta_iface_container}}.{{PARAMS.proxy_traffic_vlan}} -s 1.1.1.254 00:50:56:8c:86:c3",
                    "ip route add {{PARAMS.ta_subnet}} via 1.1.1.254 dev {{PARAMS.ta_iface_container}}.{{PARAMS.proxy_traffic_vlan}}",

                    "ip link set dev {{PARAMS.tb_iface_container}} up",
                    "ifconfig {{PARAMS.tb_iface_container}} hw ether 00:50:56:8c:86:c3",
                    "sysctl net.ipv4.conf.{{PARAMS.tb_iface_container}}.rp_filter=0",
                    "ip link add link {{PARAMS.tb_iface_container}} name {{PARAMS.tb_iface_container}}.{{PARAMS.proxy_traffic_vlan}} type vlan id {{PARAMS.proxy_traffic_vlan}}",
                    "ip link set dev {{PARAMS.tb_iface_container}}.{{PARAMS.proxy_traffic_vlan}} up",
                    "ip addr add 2.2.2.1/24 dev {{PARAMS.tb_iface_container}}.{{PARAMS.proxy_traffic_vlan}}",
                    "arp -i {{PARAMS.tb_iface_container}}.{{PARAMS.proxy_traffic_vlan}} -s 2.2.2.254 00:50:56:8c:5a:54",
                    "ip route add {{PARAMS.tb_subnet}} via 2.2.2.254 dev {{PARAMS.tb_iface_container}}.{{PARAMS.proxy_traffic_vlan}}",

                    "iptables -t mangle -N DIVERT",
                    "iptables -t mangle -A PREROUTING -p tcp -m socket -j DIVERT",
                    "iptables -t mangle -A DIVERT -j MARK --set-mark 1",
                    "iptables -t mangle -A DIVERT -j ACCEPT",
                    "ip rule add fwmark 1 lookup 100",
                    "ip route add local 0.0.0.0/0 dev lo table 100",
                    "iptables -t mangle -A PREROUTING -i {{PARAMS.ta_iface_container}}.{{PARAMS.proxy_traffic_vlan}} -p tcp --dport 443 -j TPROXY --tproxy-mark 0x1/0x1 --on-port 883",
                    "iptables -t mangle -A PREROUTING -i {{PARAMS.tb_iface_container}}.{{PARAMS.proxy_traffic_vlan}} -p tcp --dport 443 -j TPROXY --tproxy-mark 0x1/0x1 --on-port 883",

                    "tcpdump -i {{PARAMS.ta_iface_container}} {{PARAMS.ta_tcpdump}} -w {{PARAMS.result_dir_container}}/zone-1-proxy/ta.pcap &",
                    "tcpdump -i {{PARAMS.tb_iface_container}} {{PARAMS.tb_tcpdump}} -w {{PARAMS.result_dir_container}}/zone-1-proxy/tb.pcap &"
                ]
            }
        ]
    }
    ''')

    return tlspack_cfg.render(PARAMS = cmd_args)

def process_tproxy_stats (result_dir):
    pass



def add_mcert_params (cmd_parser):
    pass

def process_mcert_template (cmd_args):
    tlspack_cfg = jinja2.Template('''
    {
        "tgen_app" : "mcert",
        "zones" : [
            {% set ns = namespace(cs_grp_count=0, srv_count=0) %}
            {%- for zone_id in range(1, PARAMS.zones+1) %}
                {
                    "zone_label" : "zone-{{zone_id}}-client",
                    "enable" : 1,
                    "app_list" : [
                        {
                            "app_type" : "tls_client",
                            "app_label" : "tls_client_1",
                            "enable" : 1,
                            "conn_per_sec" : {{PARAMS.cps}},
                            "max_pending_conn_count" : {{PARAMS.max_pipeline}},
                            "max_active_conn_count" : {{PARAMS.max_active}},
                            "total_conn_count" : {{PARAMS.total_conn_count}},
                            "cs_grp_list" : [
                                {% set ns.cs_grp_count = 0 %}
                                {%- for tls_ver in ['sslv3', 'tls1', 'tls1_1', 'tls1_2', 'tls1_3'] %}
                                    {%- if (tls_ver == 'sslv3' and PARAMS.sslv3) 
                                            or (tls_ver == 'tls1' and PARAMS.tls1) 
                                            or (tls_ver == 'tls1_1' and PARAMS.tls1_1) 
                                            or (tls_ver == 'tls1_2' and PARAMS.tls1_2) 
                                            or (tls_ver == 'tls1_3' and PARAMS.tls1_3) %}
                                        {{ "," if ns.cs_grp_count }}
                                        {% set ns.cs_grp_count = ns.cs_grp_count+1 %}
                                        {
                                            "cs_grp_label" : "cs_grp_{{loop.index}}",
                                            "enable" : 1,
                                            "srv_ip"   : "14.2{{zone_id}}.51.{{loop.index}}",
                                            "srv_port" : 443,
                                            "clnt_ip_begin" : "12.2{{zone_id}}.51.{{1+loop.index0*10}}",
                                            "clnt_ip_end" : "12.2{{zone_id}}.51.{{loop.index*10}}",
                                            "clnt_port_begin" : 5000,
                                            "clnt_port_end" : 65000,
                                            "cipher" : "{{PARAMS.cipher}}",
                                            "tls_version" : "{{tls_ver}}",
                                            "close_type" : "fin",
                                            "close_notify" : "no_send",
                                            "app_rcv_buff" : {{PARAMS.app_rcv_buff}},
                                            "app_snd_buff" : {{PARAMS.app_snd_buff}},
                                            "write_chunk" : {{PARAMS.app_next_write}},
                                            "tcp_rcv_buff" : {{PARAMS.tcp_rcv_buff}},
                                            "tcp_snd_buff" : {{PARAMS.tcp_snd_buff}},
                                            "cs_data_len" : {{PARAMS.app_cs_data_len}},
                                            "sc_data_len" : {{PARAMS.app_sc_data_len}},
                                            "cs_start_tls_len" : 0,
                                            "sc_start_tls_len" : 0
                                        }
                                    {%- endif %}
                                {%- endfor %}                         
                            ]
                        }
                    ],

                    "zone_cmds" : [
                        "ip link set dev {{PARAMS.na_iface_container}} up",
                        "ifconfig {{PARAMS.na_iface_container}} hw ether {{PARAMS.client_mac_seed}}:{{'{:02x}'.format(zone_id)}}",
                        "ip route add default dev {{PARAMS.na_iface_container}} table 200",
                        "ip -4 route add local 12.2{{zone_id}}.51.0/24 dev lo",
                        "ip rule add from 12.2{{zone_id}}.51.0/24 table 200",
                        "tcpdump -i {{PARAMS.na_iface_container}} {{PARAMS.tcpdump}} -w {{PARAMS.result_dir_container}}/zone-{{zone_id}}-client/init.pcap &"
                    ]
                }
                ,
                {
                    "zone_label" : "zone-{{zone_id}}-server",
                    "enable" : 1,
                    "iface" : "{{PARAMS.iface_container}}",
                    "tcpdump" : "{{PARAMS.tcpdump}}",
                    "app_list" : [
                        {
                            "app_type" : "tls_server",
                            "app_label" : "tls_server_1",
                            "enable" : 1,
                            "srv_list" : [
                                {% set ns.srv_count = 0 %}
                                {%- for tls_ver in ['sslv3', 'tls1', 'tls1_1', 'tls1_2', 'tls1_3'] %}
                                    {%- if (tls_ver == 'sslv3' and PARAMS.sslv3) 
                                            or (tls_ver == 'tls1' and PARAMS.tls1) 
                                            or (tls_ver == 'tls1_1' and PARAMS.tls1_1) 
                                            or (tls_ver == 'tls1_2' and PARAMS.tls1_2) 
                                            or (tls_ver == 'tls1_3' and PARAMS.tls1_3) %}
                                        {{ "," if ns.srv_count }}
                                        {% set ns.srv_count = ns.srv_count+1 %}
                                        {
                                            "srv_label" : "srv_{{loop.index}}",
                                            "enable" : 1,
                                            "emulation_id" : 0,
                                            "srv_ip" : "14.2{{zone_id}}.51.{{loop.index}}",
                                            "srv_port" : 443,
                                            "srv_cert" : "{{PARAMS.server_cert}}",
                                            "srv_key" : "{{PARAMS.server_key}}",
                                            "cipher" : "{{PARAMS.cipher}}",
                                            "tls_version" : "{{tls_ver}}",
                                            "close_type" : "fin",
                                            "close_notify" : "no_send",
                                            "app_rcv_buff" : {{PARAMS.app_rcv_buff}},
                                            "app_snd_buff" : {{PARAMS.app_snd_buff}},
                                            "write_chunk" : {{PARAMS.app_next_write}},
                                            "tcp_rcv_buff" : {{PARAMS.tcp_rcv_buff}},
                                            "tcp_snd_buff" : {{PARAMS.tcp_snd_buff}},
                                            "cs_data_len" : {{PARAMS.app_cs_data_len}},
                                            "sc_data_len" : {{PARAMS.app_sc_data_len}},
                                            "cs_start_tls_len" : 0,
                                            "sc_start_tls_len" : 0
                                        }
                                    {%- endif %}
                                {%- endfor %}
                            ]
                        }
                    ],

                    "zone_cmds" : [
                        "ip link set dev {{PARAMS.nb_iface_container}} up",
                        "ifconfig {{PARAMS.nb_iface_container}} hw ether {{PARAMS.server_mac_seed}}:{{'{:02x}'.format(zone_id)}}",
                        "ip route add default dev {{PARAMS.nb_iface_container}} table 200",
                        "ip -4 route add local 14.2{{zone_id}}.51.0/24 dev lo",
                        "ip rule add from 14.2{{zone_id}}.51.0/24 table 200",
                        "tcpdump -i {{PARAMS.nb_iface_container}} {{PARAMS.tcpdump}} -w {{PARAMS.result_dir_container}}/zone-{{zone_id}}-server/init.pcap &"
                    ]
                }
                {{ "," if not loop.last }}
            {%- endfor %}
        ]
    }
    ''')

    return tlspack_cfg.render(PARAMS = cmd_args)

def process_mcert_stats(result_dir):
    ev_sockstats_client_list = []
    ev_sockstats_server_list = []

    result_dir_contents = []
    try:
        result_dir_contents = os.listdir(result_dir)
    except:
        pass

    for zone_dir in result_dir_contents:
        zone_dir_path = os.path.join(result_dir, zone_dir)
        if os.path.isdir(zone_dir_path):
            ev_sockstats_json_file = os.path.join (zone_dir_path
                                            , 'ev_sockstats.json')
            try:
                with open(ev_sockstats_json_file) as f:
                    stats_j = json.load(f)
                    if zone_dir.endswith('-client'):
                        ev_sockstats_client_list.append (stats_j)
                    if zone_dir.endswith('-server'):
                        ev_sockstats_server_list.append (stats_j)
            except:
                ev_sockstats_client_list = []
                ev_sockstats_server_list = []
                break

    if ev_sockstats_client_list:
        ev_sockstats = ev_sockstats_client_list.pop()
        while ev_sockstats_client_list:
            next_ev_sockstats = ev_sockstats_client_list.pop()
            for k, v in next_ev_sockstats.items():
                ev_sockstats[k] += v
        with open(os.path.join(result_dir, 'ev_sockstats_client.json'), 'w') as f:
            json.dump(ev_sockstats, f)

    if ev_sockstats_server_list:
        ev_sockstats = ev_sockstats_server_list.pop()
        while ev_sockstats_server_list:
            next_ev_sockstats = ev_sockstats_server_list.pop()
            for k, v in next_ev_sockstats.items():
                ev_sockstats[k] += v
        with open(os.path.join(result_dir, 'ev_sockstats_server.json'), 'w') as f:
            json.dump(ev_sockstats, f)



def get_arguments ():

    arg_parser = argparse.ArgumentParser(description = 'test commands')

    subparsers = arg_parser.add_subparsers(dest='cmd_name'
                                                    ,help='sub-command help')

    cps_parser = subparsers.add_parser('cps', help='cps help')
    add_traffic_params(cps_parser)
    add_cps_params (cps_parser)

    bw_parser = subparsers.add_parser('bw', help='bw help')
    add_traffic_params(bw_parser)
    add_bw_params (bw_parser)

    mcert_parser = subparsers.add_parser('mcert', help='mcert help')
    add_traffic_params(mcert_parser)
    add_mcert_params (mcert_parser)

    tproxy_parser = subparsers.add_parser('tproxy', help='tproxy help')
    add_proxy_params (tproxy_parser)
    add_tproxy_params (tproxy_parser)

    stop_parser = subparsers.add_parser('stop', help='stop help')
    add_stop_params (stop_parser)

    status_parser = subparsers.add_parser('status', help='stop help')
    add_status_params (status_parser)

    cmd_args = arg_parser.parse_args()

    return cmd_args


if __name__ == '__main__':

    try:
        cmd_args = get_arguments ()
    except Exception as er:
        print er
        sys.exit(1)

    host_file = os.path.join (cmd_args.host_rundir, 'sys/host')
    try:
        with open(host_file) as f:
            host_info = json.load(f)
    except Exception as er:
        print er
        sys.exit(1)


    if cmd_args.cmd_name in ['cps', 'bw', 'tproxy', 'mcert']:

        cmd_args.result_dir_container = os.path.join(cmd_args.target_rundir, 'traffic', cmd_args.runtag, 'result')

        if cmd_args.cmd_name in ['cps', 'bw', 'mcert']:
            cmd_args.na_iface_container = host_info['net_iface_map'][cmd_args.na_iface]
            cmd_args.nb_iface_container = host_info['net_iface_map'][cmd_args.nb_iface]

            cmd_args.cps = cmd_args.cps / cmd_args.zones
            cmd_args.max_active = cmd_args.max_active / cmd_args.zones
            cmd_args.max_pipeline = cmd_args.max_pipeline / cmd_args.zones


            supported_cipher_names = map(lambda x : x['cipher_name']
                                                    , supported_ciphers)

            if cmd_args.cmd_name == 'cipher':
                selected_ciphers = map(lambda x : x.strip(), cmd_args.cipher.split(':'))
                for ciph in selected_ciphers:
                    if ciph not in supported_cipher_names:
                        raise Exception ('unsupported cipher - ' + ciph)
            elif cmd_args.cmd_name == 'cps':
                if cmd_args.cipher not in supported_cipher_names:
                        raise Exception ('unsupported cipher - ' + cmd_args.cipher)

        elif cmd_args.cmd_name in ['tproxy']:
            cmd_args.ta_iface_container = host_info['net_iface_map'][cmd_args.ta_iface]
            cmd_args.tb_iface_container = host_info['net_iface_map'][cmd_args.tb_iface]

        if cmd_args.cmd_name == 'cps':
            traffic_s = process_cps_template(cmd_args)
        elif cmd_args.cmd_name == 'bw':
            traffic_s = process_bw_template(cmd_args)
        elif cmd_args.cmd_name == 'tproxy':
            traffic_s = process_tproxy_template(cmd_args)
        elif cmd_args.cmd_name == 'mcert':
            traffic_s = process_mcert_template(cmd_args)

        cfg_dir, result_dir = start_traffic(host_info, cmd_args, traffic_s)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except Exception as er:
            print er
            sys.exit(1)
        
        devnull = open(os.devnull, 'w')
        while True:
            time.sleep (2)

            subprocess.call(['rsync', '-av', '--delete'
                                , cfg_dir.rstrip('/')
                                , '/var/www/html/tmp']
                                , stdout=devnull, stderr=devnull)
            
            if not is_traffic (cmd_args):
                sys.exit(0)

            if cmd_args.cmd_name == 'cps':
                process_cps_stats (result_dir)
            elif cmd_args.cmd_name == 'bw':
                process_bw_stats (result_dir)
            elif cmd_args.cmd_name == 'tproxy':
                process_tproxy_stats (result_dir);
            elif cmd_args.cmd_name == 'mcert':
                process_mcert_stats (result_dir);

    elif cmd_args.cmd_name == 'stop':
        stop_traffic (host_info, cmd_args)

    elif cmd_args.cmd_name == 'status':
        show_traffic (host_info, cmd_args)



