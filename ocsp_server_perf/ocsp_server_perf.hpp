#ifndef __OCSP_SERVER_PERF_H__
#define __OCSP_SERVER_PERF_H__

#include "app.hpp"

#include "llhttp.h"


#define DEFAULT_WRITE_CHUNK 1200
#define DEFAULT_WRITE_BUFF_LEN 1000000
#define DEFAULT_READ_BUFF_LEN 1000000

class ocsp_server_perf_srv_grp : public ev_app_srv_grp 
{
public:
    ocsp_server_perf_srv_grp (json jcfg
                        , app_stats* parent_stats, app_stats* zone_stats) 
                        : ev_app_srv_grp (jcfg, parent_stats, zone_stats) 
    {
    }
};

class ocsp_server_perf_app : public app
{
public:
    ocsp_server_perf_app(json app_json
                    , app_stats* zone_app_stats);

    ~ocsp_server_perf_app();

    void run_iter(bool tick_sec);

    ev_socket* alloc_socket();
    void free_socket(ev_socket* ev_sock);

public:
    std::vector<ocsp_server_perf_srv_grp*> m_srv_groups;
};

class ocsp_server_perf_socket : public ev_socket
{
public:
    ocsp_server_perf_socket()
    {
        m_bytes_written = 0;
        m_bytes_read = 0;
        m_read_buffer_len = DEFAULT_READ_BUFF_LEN;
        m_read_buffer = (char*) malloc (m_read_buffer_len);
    };

    virtual ~ocsp_server_perf_socket()
    {
        if (m_read_buffer){
            free (m_read_buffer);
        }
    };

    void on_establish ();
    void on_write ();
    void on_wstatus (int bytes_written, int write_status);
    void on_read ();
    void on_rstatus (int bytes_read, int read_status);
    void on_finish ();

public:
    ocsp_server_perf_srv_grp* m_srv_grp;
    ocsp_server_perf_app* m_app;
    ocsp_server_perf_socket* m_lsock;

    int m_bytes_written;
    int m_bytes_read;
    char* m_read_buffer;
    int m_read_buffer_len;

    llhttp_t m_parser;
    llhttp_settings_t m_settings;

private:

};

#endif