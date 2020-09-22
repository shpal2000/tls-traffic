#include "rpc_server.hpp"


rpc_server_app::rpc_server_app(const char* srv_ip
                                , u_short srv_port
                                , rpc_server_stats* srv_stats)
{
    m_stats_arr.push_back(srv_stats);

    ev_socket::set_sockaddr (&m_srvr_addr, srv_ip, htons(srv_port));
    m_sock_opt.rcv_buff_len = 0;
    m_sock_opt.snd_buff_len = 0;
    
    rpc_server_socket* srv_socket 
        = (rpc_server_socket*) new_tcp_listen (&m_srvr_addr
                                                , 100
                                                , &m_stats_arr
                                                , &m_sock_opt);
    if (srv_socket){
        srv_socket->m_app = this;
    }else {
        //todo error handling
    }
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
    disable_wr_notification ();
}

void rpc_server_socket::on_write ()
{
    int resp_len = m_app->rpc_handler(m_read_buff, m_write_buff, m_max_buff_len);

     if (resp_len > 0)
     {
         write_next_data (m_write_buff, 0, resp_len, false);
     }else{
        abort();  
     }
}

void rpc_server_socket::on_wstatus (int /* bytes_written */, int write_status)
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
    if (m_read_buff_off < m_max_buff_len)
    {
        read_next_data(m_read_buff
                        , m_read_buff_off
                        , m_max_buff_len - m_read_buff_off
                        , 1);
    }
    else 
    {
        abort ();
    }
}

void rpc_server_socket::on_rstatus (int bytes_read, int read_status)
{
    if (bytes_read == 0) 
    {
        if (read_status != READ_STATUS_TCP_CLOSE) {
            abort ();
        }
        else {
            enable_wr_notification ();
        }
    } 
    else
    {
        m_read_buff_off += bytes_read;
        m_read_buff [m_read_buff_off] = '\0';
    }
}

void rpc_server_socket::on_finish ()
{
}
