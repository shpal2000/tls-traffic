#include "tcp_proxy.hpp"

tcp_proxy_app::tcp_proxy_app(json app_json
                                , tcp_proxy_stats* zone_app_stats
                                , ev_sockstats* zone_sock_stats)
{
    proxy_config_init (app_json);

    m_app_stats = new tcp_proxy_stats();

    auto proxy_list = app_json["proxy_list"];
    for (auto it = proxy_list.begin(); it != proxy_list.end(); ++it)
    {
        auto proxy_cfg = it.value ();

        const char* proxy_label 
            = proxy_cfg["proxy_label"].get<std::string>().c_str();
        
        int proxy_enable = proxy_cfg["enable"].get<int>();
        if (proxy_enable == 0) {
            continue;
        }

        tcp_proxy_stats* proxy_stats = new tcp_proxy_stats();
        set_app_stats (proxy_stats, proxy_label);

        std::vector<ev_sockstats*> *proxy_stats_arr
            = new std::vector<ev_sockstats*> ();

        proxy_stats_arr->push_back (proxy_stats);
        proxy_stats_arr->push_back (m_app_stats);
        proxy_stats_arr->push_back (zone_app_stats);
        proxy_stats_arr->push_back (zone_sock_stats);

        tcp_proxy_grp* next_proxy_grp
            = new tcp_proxy_grp (proxy_cfg, proxy_stats_arr);

        m_proxy_groups.push_back (next_proxy_grp);
    }

    for (auto proxy_grp : m_proxy_groups)
    {
        tp_socket* proxy_socket 
            = (tp_socket*) new_tcp_listen (&proxy_grp->m_proxy_addr
                                                    , 10000
                                                    , proxy_grp->m_stats_arr
                                                    , &proxy_grp->m_sock_opt);
        if (proxy_socket) 
        {
            proxy_socket->m_app = this;
            proxy_socket->m_proxy_grp = proxy_grp;
        }
        else
        {
            //todo error handling
        }
    }
}

tcp_proxy_app::~tcp_proxy_app()
{

}

void tcp_proxy_app::run_iter(bool tick_sec)
{
    ev_app::run_iter (tick_sec);

    if (tick_sec)
    {
        m_app_stats->tick_sec();
    }
}

ev_socket* tcp_proxy_app::alloc_socket()
{
    return new tp_socket();
}

void tcp_proxy_app::free_socket(ev_socket* ev_sock)
{
    delete ev_sock;
}

void tp_socket::on_establish ()
{
    if (m_session == nullptr) // accepted socket; new session
    {
        tp_socket* server_socket = this;
        tp_session* new_sess = new tp_session();
        tcp_proxy_app* proxy_app = ((tp_socket*)get_parent())->m_app;
        tcp_proxy_grp* proxy_grp = ((tp_socket*)get_parent())->m_proxy_grp;

        if (new_sess)
        {
            tp_socket* client_socket 
                    = (tp_socket*) proxy_app->new_tcp_connect (get_remote_addr()
                                                        , get_local_addr()
                                                        , proxy_grp->m_stats_arr
                                                        , NULL
                                                        , &proxy_grp->m_sock_opt);
            if (client_socket)
            {
                server_socket->m_session = new_sess;
                client_socket->m_session = new_sess;

                m_session->m_server_sock = server_socket;
                m_session->m_client_sock = client_socket;

                server_socket->m_app = proxy_app;
                client_socket->m_app = proxy_app;

                server_socket->m_proxy_grp = proxy_grp;
                client_socket->m_proxy_grp = proxy_grp;
            }
            else
            {
                //todo error handling
                delete new_sess;
                server_socket->abort();
            }
        }
        else
        {
            //todo error handling
            server_socket->abort();
        }
    }
    else //client session
    {
        // printf ("on_establish - client\n");
        m_session->m_session_established = true;
    }
}

void tp_socket::on_write ()
{
    if (m_session->m_session_established)
    {
        if (m_session->m_client_sock == this)
        {
            if ( not m_session->m_server_rbuffs.empty () )
            {
                ev_buff* wr_buff = m_session->m_server_rbuffs.front ();
                m_session->m_server_rbuffs.pop ();
                write_next_data (wr_buff->m_buff, 0, wr_buff->m_data_len, false);
                m_session->m_client_current_wbuff = wr_buff;
            }
        }
        else
        {
            if ( not m_session->m_client_rbuffs.empty () )
            {
                ev_buff* wr_buff = m_session->m_client_rbuffs.front ();
                m_session->m_client_rbuffs.pop ();
                write_next_data (wr_buff->m_buff, 0, wr_buff->m_data_len, false);
                m_session->m_server_current_wbuff = wr_buff;
            }
        }   
    }
}

void tp_socket::on_wstatus (int /*bytes_written*/, int write_status)
{
    if (m_session->m_client_sock == this)
    {
        delete m_session->m_client_current_wbuff;
        m_session->m_client_current_wbuff = nullptr;
    }
    else
    {
        delete m_session->m_server_current_wbuff;
        m_session->m_server_current_wbuff = nullptr;
    }

    if (write_status == WRITE_STATUS_NORMAL)
    {
        //todo
    }
    else
    {
        //todo error handling
        if (m_session->m_client_sock) {
            m_session->m_client_sock->abort ();
        }

        if (m_session->m_server_sock) {
            m_session->m_server_sock->abort();
        }
    }
}

void tp_socket::on_read ()
{
    ev_buff* rd_buff = new ev_buff(2048);
    if (rd_buff && rd_buff->m_buff)
    {
        if (m_session->m_client_sock == this)
        {
            m_session->m_client_current_rbuff = rd_buff;
        }
        else
        {
            m_session->m_server_current_rbuff = rd_buff;
        }

        read_next_data (rd_buff->m_buff, 0, rd_buff->m_buff_len, true);
    }
    else
    {
        //todo error handling
    }
}

void tp_socket::on_rstatus (int bytes_read, int read_status)
{
    if (bytes_read == 0) 
    {
        if (m_session->m_client_sock == this)
        {
            delete m_session->m_client_current_rbuff;

            if (read_status == READ_STATUS_TCP_CLOSE) 
            {
                if (m_session->m_server_sock){
                    m_session->m_server_sock->write_close();
                }
            }
            else
            {
                if (m_session->m_client_sock) {
                    m_session->m_client_sock->abort ();
                }

                if (m_session->m_server_sock) {
                    m_session->m_server_sock->abort();
                }
            }
        } 
        else
        {
            delete m_session->m_server_current_rbuff;

            if (read_status == READ_STATUS_TCP_CLOSE) 
            {
                if (m_session->m_client_sock) {
                    m_session->m_client_sock->write_close();
                }
            }
            else
            {
                if (m_session->m_client_sock) {
                    m_session->m_client_sock->abort ();
                }

                if (m_session->m_server_sock) {
                    m_session->m_server_sock->abort();
                }
            }
        }
    } 
    else 
    {
        if (m_session->m_client_sock == this)
        { 
            m_session->m_client_current_rbuff->m_data_len = bytes_read;
            m_session->m_client_rbuffs.push (m_session->m_client_current_rbuff);
        } 
        else
        {
            m_session->m_server_current_rbuff->m_data_len = bytes_read;
            m_session->m_server_rbuffs.push (m_session->m_server_current_rbuff);
        }
    }
}

void tp_socket::on_finish ()
{
    if (m_session)
    {
        if (m_session->m_client_sock == this)
        {
            m_session->m_client_sock = nullptr;
        }
        else
        {
            m_session->m_server_sock = nullptr;
        }

        if (not m_session->m_client_sock && not m_session->m_server_sock)
        {
            delete m_session;
        }
    }
}