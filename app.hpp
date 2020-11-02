#ifndef __TLSPACK_APP__H
#define __TLSPACK_APP__H

#include "ev_app.hpp"

#include <stdint.h>
#include <errno.h>
#include <unistd.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509.h>
#include <openssl/pem.h>
#include <iostream>
#include <fstream>
#include<sstream>
#include <queue>
#include <cstring>
#include <string>
#include <thread>
#include <chrono>
#include <map>
#include <random>
#include <inttypes.h>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

enum enum_close_type { close_fin=1, close_reset };

enum enum_close_notify { close_notify_no_send=1
                           , close_notify_send
                           ,  close_notify_send_recv};
                           
enum enum_tls_version { sslv3=0, tls1, tls1_1, tls1_2, tls1_3, tls_all};


#define MAX_APP_TYPE_NAME 1024
#define MAX_CHUNK_SIZES_ARRAY_LEN 30

struct app_stats : public ev_sockstats
{
    uint64_t sslResumptionInit;
    uint64_t sslResumptionInitHit;
    uint64_t sslResumptionInitMiss;

    uint64_t sslResumptionRecv;
    uint64_t sslResumptionRecvHit;
    uint64_t sslResumptionRecvMiss;

    static void dump_json_ev_sockstats (json& j, ev_sockstats* stats)
    {
        j["socketCreate"] = stats->socketCreate;
        j["socketCreateFail"] = stats->socketCreateFail;
        j["socketListenFail"] = stats->socketListenFail;
        j["socketReuseSet"] = stats->socketReuseSet;
        j["socketReuseSetFail"] = stats->socketReuseSetFail;
        j["socketIpTransparentSet"] = stats->socketIpTransparentSet;
        j["socketIpTransparentSetFail"] = stats->socketIpTransparentSetFail;
        j["socketLingerSet"] = stats->socketLingerSet;
        j["socketLingerSetFail"] = stats->socketLingerSetFail;
        j["socketBindIpv4"] = stats->socketBindIpv4;
        j["socketBindIpv4Fail"] = stats->socketBindIpv4Fail;
        j["socketBindIpv6"] = stats->socketBindIpv6;
        j["socketBindIpv6Fail"] = stats->socketBindIpv6Fail;

        j["socketConnectEstablishFail"] = stats->socketConnectEstablishFail;
        j["socketConnectEstablishFail2"] = stats->socketConnectEstablishFail2;

        j["tcpConnInit"] = stats->tcpConnInit;
        j["tcpConnInitInUse"] = stats->tcpConnInitInUse;
        j["tcpConnInitInSec"] = stats->tcpConnInitInSec;
        j["tcpConnInitRate"] = stats->tcpConnInitRate;
        j["tcpConnInitSuccess"] = stats->tcpConnInitSuccess;
        j["tcpConnInitSuccessInSec"] = stats->tcpConnInitSuccessInSec;
        j["tcpConnInitSuccessRate"] = stats->tcpConnInitSuccessRate;
        j["tcpConnInitFail"] = stats->tcpConnInitFail;
        j["tcpConnInitFailImmediateEaddrNotAvail"] = stats->tcpConnInitFailImmediateEaddrNotAvail;
        j["tcpConnInitFailImmediateOther"] = stats->tcpConnInitFailImmediateOther;
        j["tcpConnInitProgress"] = stats->tcpConnInitProgress;
        j["tcpWriteFail"] = stats->tcpWriteFail;
        j["tcpWriteReturnsZero"] = stats->tcpWriteReturnsZero;
        j["tcpReadFail"] = stats->tcpReadFail;

        j["tcpListenStart"] = stats->tcpListenStart;
        j["tcpListenStop"] = stats->tcpListenStop;
        j["tcpListenStartFail"] = stats->tcpListenStartFail;
        j["tcpAcceptFail"] = stats->tcpAcceptFail;
        j["tcpAcceptSuccess"] = stats->tcpAcceptSuccess;
        j["tcpAcceptSuccessInSec"] = stats->tcpAcceptSuccessInSec;
        j["tcpAcceptSuccessRate"] = stats->tcpAcceptSuccessRate;

        j["tcpLocalPortAssignFail"] = stats->tcpLocalPortAssignFail;
        j["tcpPollRegUnregFail"] = stats->tcpPollRegUnregFail;

        j["sslConnInit"] = stats->sslConnInit;
        j["sslConnInitInSec"] = stats->sslConnInitInSec;
        j["sslConnInitRate"] = stats->sslConnInitRate;
        j["sslConnInitSuccess"] = stats->sslConnInitSuccess;
        j["sslConnInitSuccessInSec"] = stats->sslConnInitSuccessInSec;
        j["sslConnInitSuccessRate"] = stats->sslConnInitSuccessRate;
        j["sslConnInitFail"] = stats->sslConnInitFail;
        j["sslConnInitProgress"] = stats->sslConnInitProgress;
        j["sslAcceptSuccess"] = stats->sslAcceptSuccess;
        j["sslAcceptSuccessInSec"] = stats->sslAcceptSuccessInSec;
        j["sslAcceptSuccessRate"] = stats->sslAcceptSuccessRate;

        j["tcpConnStructNotAvail"] = stats->tcpConnStructNotAvail;
        j["tcpListenStructNotAvail"] = stats->tcpListenStructNotAvail;
        j["appSessStructNotAvail"] = stats->appSessStructNotAvail;
        j["tcpInitServerFail"] = stats->tcpInitServerFail;
        j["tcpGetSockNameFail"] = stats->tcpGetSockNameFail;

        j["tcpActiveConns"] = stats->tcpActiveConns;
    }

    virtual void dump_json (json& j)
    {
        dump_json_ev_sockstats (j, this);

        j["sslResumptionInit"] = sslResumptionInit;
        j["sslResumptionInitHit"] = sslResumptionInitHit;
        j["sslResumptionInitMiss"] = sslResumptionInitMiss;

        j["sslResumptionRecv"] = sslResumptionRecv;
        j["sslResumptionRecvHit"] = sslResumptionRecvHit;
        j["sslResumptionRecvMiss"] = sslResumptionRecvMiss;

    };

};

typedef std::map<std::string, app_stats*> ev_stats_map;

class ev_app_conn_grp
{
public:
    ev_socket_opt m_sock_opt;
    std::vector<ev_sockstats*> m_stats_arr;
    app_stats m_grp_stats;

    app_stats* get_stats () {return &m_grp_stats;}
    
    ev_app_conn_grp (json jcfg, app_stats* parent_stats, app_stats* zone_stats) {
        m_sock_opt.rcv_buff_len = jcfg["tcp_rcv_buff"].get<uint32_t>();
        m_sock_opt.snd_buff_len = jcfg["tcp_snd_buff"].get<uint32_t>();

        m_stats_arr.push_back (&m_grp_stats);
        m_stats_arr.push_back (parent_stats);
        m_stats_arr.push_back (zone_stats);
    }
};

class ev_app_cs_grp : public ev_app_conn_grp
{
public:

    std::vector<ev_sockaddrx*> m_clnt_addr_pool;
    int m_clnt_addr_index;
    int m_clnt_addr_count;

    ev_sockaddr m_srvr_addr;
    
    ev_app_cs_grp (json jcfg, app_stats* parent_stats, app_stats* zone_stats)
                            : ev_app_conn_grp (jcfg, parent_stats, zone_stats)
    {

        auto srv_ip = jcfg["srv_ip"].get<std::string>();
        u_short srv_port = jcfg["srv_port"].get<u_short>();
        auto ip_begin = jcfg["clnt_ip_begin"].get<std::string>();
        auto ip_end = jcfg["clnt_ip_end"].get<std::string>();
        u_short port_begin = jcfg["clnt_port_begin"].get<u_short>();
        u_short port_end = jcfg["clnt_port_end"].get<u_short>();

        m_clnt_addr_index = 0;
        m_clnt_addr_count = 0;

        char next_ip[128];
        strcpy (next_ip, ip_begin.c_str());
        ev_sockaddrx* next_addr = new ev_sockaddrx (port_begin, port_end);
        ev_socket::set_sockaddr (&next_addr->m_addr, next_ip, 0);
        m_clnt_addr_pool.push_back(next_addr);
        m_clnt_addr_count++;

        while (strcmp(next_ip, ip_end.c_str()))
        {
            next_addr = new ev_sockaddrx (port_begin, port_end);
            ev_socket::get_nextip_str (next_ip, 1, next_ip);
            ev_socket::set_sockaddr (&next_addr->m_addr, next_ip, 0);
            m_clnt_addr_pool.push_back(next_addr);
            m_clnt_addr_count++;
        }

        ev_socket::set_sockaddr (&m_srvr_addr, srv_ip.c_str(), htons(srv_port));

    }

    ev_sockaddr* get_server_addr () {return &m_srvr_addr;};
    ev_sockaddrx* get_next_clnt_addr () 
    {
        ev_sockaddrx* ret = nullptr;
        if (m_clnt_addr_count > 0)
        {
            ret = m_clnt_addr_pool[m_clnt_addr_index];
            m_clnt_addr_index++;
            if (m_clnt_addr_index == m_clnt_addr_count)
            {
                m_clnt_addr_index = 0;
            }
            u_short port = ret->m_portq->get_port();
            if (port)
            {
                ev_socket::set_sockaddr_port(&ret->m_addr, port);
            }
            else
            {
                ret = nullptr;
            }
        }
        return ret;
    };
};

class ev_app_srv_grp : public ev_app_conn_grp
{
public:

    ev_sockaddr m_srvr_addr;

    ev_app_srv_grp (json jcfg, app_stats* parent_stats, app_stats* zone_stats)
                        : ev_app_conn_grp (jcfg, parent_stats, zone_stats)
    {
        auto srv_ip = jcfg["srv_ip"].get<std::string>();
        u_short srv_port = jcfg["srv_port"].get<u_short>();
        ev_socket::set_sockaddr (&m_srvr_addr, srv_ip.c_str(), htons(srv_port));
    }
};

class ev_app_proxy_grp : public ev_app_conn_grp
{
public:

    ev_sockaddr m_proxy_addr;
    int m_proxy_type;

    ev_app_proxy_grp (json jcfg, app_stats* parent_stats, app_stats* zone_stats)
                            : ev_app_conn_grp (jcfg, parent_stats, zone_stats)
    {
        auto proxy_ip = jcfg["proxy_ip"].get<std::string>();
        u_short proxy_port = jcfg["proxy_port"].get<u_short>();
        ev_socket::set_sockaddr (&m_proxy_addr, proxy_ip.c_str(), htons(proxy_port));

        m_proxy_type = jcfg["proxy_type_id"].get<u_short>();
    }
};

class app : public ev_app
{
public:
    app()
    {
        m_next_chunk_index = 0;
        m_next_chunk_shift = 0;
        m_stop = false;
    }
    virtual ~app()
    {
    }

    virtual void run_iter(bool tick_sec)
    {
        ev_app::run_iter (tick_sec);
    }

    void set_stop(){
        m_stop = true;
    }

    bool is_zero_conn_state(){
        if (m_app_stats.tcpConnInitInUse == 0) {
            return true;
        }
        return false;
    }

    ev_stats_map* get_app_stats_map ()
    {
        return &m_stats_map;
    } 
    
    app_stats* get_app_stats (const char* stats_label="")
    {
        if (strcmp(stats_label, "") == 0)
            return &m_app_stats;

        return m_stats_map[stats_label];
    };

    void set_app_stats (app_stats* stats, const char* stats_label)
    {
        m_stats_map.insert(ev_stats_map::value_type(stats_label, stats));
    }

    const char* get_app_type () {return m_app_type;};
    void set_app_type (const char* app_type) {strcpy (m_app_type, app_type);};

    const char* get_app_label () {return m_app_label;};
    void set_app_label(const char* app_label) {strcpy (m_app_label,app_label);};

    int get_new_conn_count ()
    {
        int n = 0;

        if (not m_stop) {
            if (m_client_curr_conn_count == 0){
                m_conn_init_time = std::chrono::steady_clock::now ();
                n = 1;
            } else if ((m_client_total_conn_count == 0) 
                        || (m_client_curr_conn_count < m_client_total_conn_count)) {

                if ( (m_client_max_active_conn_count == 0) || (m_app_stats.tcpConnInitInUse < m_client_max_active_conn_count) )  {
                    auto t = std::chrono::steady_clock::now();
                    auto span = std::chrono::duration_cast<std::chrono::nanoseconds>
                                                    (t - m_conn_init_time).count();
                    uint64_t c = (m_client_cps * span) / 1000000000;
                    if (c > m_client_curr_conn_count ) {
                        n = 1;
                    }
                }
            }
        }

        return n;
    }

    void client_config_init (json jcfg) 
    {
        m_client_cps = jcfg["conn_per_sec"].get<uint32_t>();

        m_client_total_conn_count 
            = jcfg["total_conn_count"].get<uint64_t>();

        m_client_max_active_conn_count 
            = jcfg["max_active_conn_count"].get<uint32_t>();

        m_client_max_pending_conn_count 
            = jcfg["max_pending_conn_count"].get<uint32_t>();
    
        m_client_curr_conn_count = 0;
    }

    void server_config_init (json /*jcfg*/)
    {
        
    }

    void proxy_config_init (json /*jcfg*/)
    {
        
    }

    int get_next_chunk_size () 
    {
        if (m_next_chunk_index == MAX_CHUNK_SIZES_ARRAY_LEN) {
            m_next_chunk_index = 0;
            m_next_chunk_shift++;
            if (m_next_chunk_shift == 10){
                m_next_chunk_shift = 0;
            }
        }
        return m_chunk_sizes[m_next_chunk_index] + m_next_chunk_shift;
    }

private:
    ev_stats_map m_stats_map;
    char m_app_type[MAX_APP_TYPE_NAME];
    char m_app_label[MAX_APP_TYPE_NAME];
    std::chrono::steady_clock::time_point m_conn_init_time;
    int m_chunk_sizes [MAX_CHUNK_SIZES_ARRAY_LEN] = { 
        1, 2, 256, 257, 512, 513, 801, 1023, 1024, 1256, 
        1513, 1800, 2512, 3801, 4006, 5023, 5024, 6023, 7024, 7001, 
        8256, 9800, 10000, 11000, 12000, 13000, 14000, 15000, 16383, 16384  
    };
    int m_next_chunk_index;
    int m_next_chunk_shift;
    bool m_stop;

protected:
    uint32_t m_client_cps;
    uint64_t m_client_curr_conn_count;
    uint64_t m_client_total_conn_count;
    uint32_t m_client_max_active_conn_count;
    uint32_t m_client_max_pending_conn_count;
    app_stats m_app_stats;
};

typedef app* (*app_maker_t) (json, ev_sockstats*);

#define inc_t_stats(__stat_name) \
{ \
    inc_app_stats(this,app_stats,__stat_name); \
}

#define dec_t_stats(__stat_name) \
{ \
    dec_app_stats(this,app_stats,__stat_name); \
}

#endif