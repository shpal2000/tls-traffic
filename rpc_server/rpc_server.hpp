#ifndef __RPC_SERVER_H__
#define __RPC_SERVER_H__

#include "app.hpp"

class rpc_server_app : public app
{
public:
    rpc_server_app();
    ~rpc_server_app();

    void run_iter(bool tick_sec);

    ev_socket* alloc_socket();
    void free_socket(ev_socket* ev_sock);
};

class rpc_server_socket : public ev_socket
{
public:
    rpc_server_socket()
    {

    };

    virtual ~rpc_server_socket()
    {

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
};

#endif