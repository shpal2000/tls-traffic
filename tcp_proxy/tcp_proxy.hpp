#ifndef __TCP_PROXY__H
#define __TCP_PROXY__H

#include "app.hpp"

class tcp_proxy_grp : public ev_app_proxy_grp 
{
    public:
    tcp_proxy_grp (json jcfg
                        , std::vector<ev_sockstats*> *stats_arr) 
                    
                    : ev_app_proxy_grp (jcfg, stats_arr) 
    {
        
    }
};

struct tcp_proxy_stats_data : app_stats
{
    uint64_t tcp_proxy_stats_1;
    uint64_t tcp_proxy_stats_100;

    virtual void dump_json (json &j)
    {
        app_stats::dump_json (j);
        
        j["tcp_proxy_stats_1"] = tcp_proxy_stats_1;
        j["tcp_proxy_stats_100"] = tcp_proxy_stats_100;
    }

    virtual ~tcp_proxy_stats_data() {};
};

struct tcp_proxy_stats : tcp_proxy_stats_data
{
    tcp_proxy_stats () : tcp_proxy_stats_data () {}
};

class tcp_proxy_app : public app
{
public:
    tcp_proxy_app(json app_json
                    , tcp_proxy_stats* zone_app_stats
                    , ev_sockstats* zone_sock_stats);

    ~tcp_proxy_app();

    void run_iter(bool tick_sec);
    
    ev_socket* alloc_socket();
    void free_socket(ev_socket* ev_sock);

public:
    std::vector<tcp_proxy_grp*> m_proxy_groups;
};

class tp_session;
class tp_socket : public ev_socket
{
public:
    tp_socket()
    {
        m_app = nullptr;
        m_session = nullptr;
    };

    virtual ~tp_socket()
    {

    };
    
    void on_establish ();
    void on_write ();
    void on_wstatus (int bytes_written, int write_status);
    void on_read ();
    void on_rstatus (int bytes_read, int read_status);
    void on_finish ();

public:
    tp_session* m_session;
    tcp_proxy_app* m_app;
    tcp_proxy_grp* m_proxy_grp;
};

class tp_session
{
public:

    tp_session()
    {
        m_server_sock = nullptr;
        m_client_sock = nullptr;
        m_session_established = false;

        m_client_current_wbuff = nullptr;
        m_server_current_wbuff = nullptr;

        m_client_current_rbuff = nullptr;
        m_server_current_rbuff = nullptr;
    }

    ~tp_session()
    {

    }
    
public:
    tp_socket* m_server_sock;
    tp_socket* m_client_sock;
    bool m_session_established;

    ev_buff* m_client_current_wbuff;
    ev_buff* m_server_current_wbuff;

    ev_buff* m_client_current_rbuff;
    ev_buff* m_server_current_rbuff;
    
    std::queue<ev_buff*> m_client_rbuffs;
    std::queue<ev_buff*> m_server_rbuffs;
};

#endif