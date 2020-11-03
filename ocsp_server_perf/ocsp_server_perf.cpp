#include "ocsp_server_perf.hpp"

int on_message_begin (llhttp_t*)
{
    return 0;
}


int on_header_field (llhttp_t*, const char *at, size_t length)
{
    puts ("on_header_field\n");
    return 0;
}


int on_header_value (llhttp_t*, const char *at, size_t length)
{
    puts ("on_header_value\n");
    return 0;
}


int on_message_complete (llhttp_t*)
{
    return 0;
}

ocsp_server_perf_app::ocsp_server_perf_app(json app_json
                                , app_stats* zone_app_stats)
{
    server_config_init (app_json);

    auto srv_list = app_json["srv_list"];
    for (auto it = srv_list.begin(); it != srv_list.end(); ++it)
    {
        auto srv_cfg = it.value ();

        auto srv_label = srv_cfg["srv_label"].get<std::string>();
        
        int srv_enable = srv_cfg["enable"].get<int>();
        if (srv_enable == 0) {
            continue;
        }

        ocsp_server_perf_srv_grp* next_srv_grp = new ocsp_server_perf_srv_grp (srv_cfg
                                            , &m_app_stats, zone_app_stats);

        set_app_stats (next_srv_grp->get_stats(), srv_label.c_str());

        m_srv_groups.push_back (next_srv_grp);
    }

    for (auto srv_grp : m_srv_groups)
    {
        ocsp_server_perf_socket* srv_socket 
            = (ocsp_server_perf_socket*) new_tcp_listen (&srv_grp->m_srvr_addr
                                                    , 10000
                                                    , &srv_grp->m_stats_arr
                                                    , &srv_grp->m_sock_opt);
        if (srv_socket) 
        {
            srv_socket->m_app = this;
            srv_socket->m_srv_grp = srv_grp;
        }
        else
        {
            //todo error handling
        }
    }
}

ocsp_server_perf_app::~ocsp_server_perf_app()
{
}

void ocsp_server_perf_app::run_iter(bool tick_sec)
{
    ev_app::run_iter (tick_sec);

    if (tick_sec)
    {
        m_app_stats.tick_sec();
    }
}

ev_socket* ocsp_server_perf_app::alloc_socket()
{
    return new ocsp_server_perf_socket();
}

void ocsp_server_perf_app::free_socket(ev_socket* ev_sock)
{
    delete ev_sock;
}

void ocsp_server_perf_socket::on_establish ()
{
    m_lsock = (ocsp_server_perf_socket*) get_parent();
    m_app = m_lsock->m_app;
    m_srv_grp = m_lsock->m_srv_grp;

    llhttp_settings_init(&m_settings);
    m_settings.on_header_field = on_header_field;
    m_settings.on_header_value = on_header_value;

    llhttp_init (&m_parser, HTTP_REQUEST, &m_settings);
}

void ocsp_server_perf_socket::on_write ()
{
}

void ocsp_server_perf_socket::on_wstatus (int bytes_written, int write_status)
{
    if (write_status == WRITE_STATUS_NORMAL) 
    {
      
    } 
    else 
    {
        abort ();
    }
}

void ocsp_server_perf_socket::on_read ()
{
    read_next_data (m_read_buffer, m_bytes_read, m_read_buffer_len - m_bytes_read, true);
}

void ocsp_server_perf_socket::on_rstatus (int bytes_read, int read_status)
{
    if (bytes_read == 0) 
    {
        if (read_status != READ_STATUS_TCP_CLOSE) {
            abort ();
        }
    } 
    else
    {
        llhttp_execute (&m_parser, m_read_buffer+m_bytes_read, bytes_read);
        m_bytes_read += bytes_read;
    }
}

void ocsp_server_perf_socket::on_finish ()
{

}







extern "C" {
    app* ocsp_server_perf (json app_json, app_stats* zone_app_stats) 
    {
        return new ocsp_server_perf_app (app_json, zone_app_stats);
    }
}
