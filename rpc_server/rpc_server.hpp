#ifndef __RPC_SERVER_H__
#define __RPC_SERVER_H__

#include "app.hpp"

struct rpc_server_stats_data : app_stats
{
    uint64_t rpc_server_stats_1;
    uint64_t rpc_server_stats_100;

    virtual void dump_json (json &j)
    {
        app_stats::dump_json (j);
        
        j["rpc_server_stats_1"] = rpc_server_stats_1;
        j["rpc_server_stats_100"] = rpc_server_stats_100;
    }

    virtual ~rpc_server_stats_data() {};
};

struct rpc_server_stats : rpc_server_stats_data
{
    rpc_server_stats () : rpc_server_stats_data () {}
};

class rpc_server_app : public app
{
public:
    rpc_server_app(const char* srv_ip
                    , u_short srv_port
                    , rpc_server_stats* srv_stats);

    ~rpc_server_app();

    void run_iter(bool tick_sec);

    ev_socket* alloc_socket();
    void free_socket(ev_socket* ev_sock);

private:
    ev_sockaddr m_srvr_addr;
    ev_socket_opt m_sock_opt;
    std::vector<ev_sockstats*> m_stats_arr;
};

class rpc_server_socket : public ev_socket
{
public:
    rpc_server_socket()
    {
        m_max_buff_len = 1024*1024;
        m_read_buff_off = 0;
        m_write_buff_off = 0;

        m_read_buff = (char*) malloc(m_max_buff_len);
        m_write_buff = (char*) malloc(m_max_buff_len);
    };

    virtual ~rpc_server_socket()
    {
        if (m_read_buff) {
            delete m_read_buff;
        }

        if (m_write_buff) {
            delete m_write_buff;
        }
    };

    void on_establish ();
    void on_write ();
    void on_wstatus (int bytes_written, int write_status);
    void on_read ();
    void on_rstatus (int bytes_read, int read_status);
    void on_finish ();

public:
    rpc_server_app* m_app;

private:
    int m_max_buff_len;
    int m_read_buff_off;
    int m_write_buff_off;
    char* m_read_buff;
    char* m_write_buff;
};

#endif