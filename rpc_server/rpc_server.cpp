#include "rpc_server.hpp"


rpc_server_app::rpc_server_app()
{
}

rpc_server_app::~rpc_server_app()
{
}

void rpc_server_app::run_iter(bool tick_sec)
{
    ev_app::run_iter (tick_sec);

    if (tick_sec)
    {
        
    }
}

ev_socket* rpc_server_app::alloc_socket()
{
    return new rpc_server_socket();
}

void rpc_server_app::free_socket(ev_socket* ev_sock)
{
    delete ev_sock;
}



void rpc_server_socket::on_establish ()
{

    m_app = ((rpc_server_socket*) get_parent())->m_app;
}

void rpc_server_socket::on_write ()
{

}

void rpc_server_socket::on_wstatus (int bytes_written, int write_status)
{
    if (write_status == WRITE_STATUS_NORMAL) 
    {
        write_close ();        
    } 
    else 
    {
        abort ();
    }
}

void rpc_server_socket::on_read ()
{
    // read_next_data
}

void rpc_server_socket::on_rstatus (int bytes_read, int read_status)
{
    if (bytes_read == 0) 
    {
        if (read_status != READ_STATUS_TCP_CLOSE) {
            abort ();
        }
    } 
    else
    {
        
    }
}

void rpc_server_socket::on_finish ()
{
}
