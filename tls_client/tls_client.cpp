#include "tls_client.hpp"

tls_client_app::tls_client_app(json app_json
                    , tls_client_stats* zone_app_stats
                    , ev_sockstats* zone_sock_stats)
{
    client_config_init (app_json);

    m_app_stats = new tls_client_stats();

    auto cs_grp_list = app_json["cs_grp_list"];
    m_cs_group_count = 0;
    m_cs_group_index = 0;
    for (auto it = cs_grp_list.begin(); it != cs_grp_list.end(); ++it)
    {
        auto cs_grp_cfg = it.value ();

        const char* cs_grp_label 
            = cs_grp_cfg["cs_grp_label"].get<std::string>().c_str();

        int cs_grp_enable = cs_grp_cfg["enable"].get<int>();
        if (cs_grp_enable == 0) {
            continue;
        }

        tls_client_stats* cs_grp_stats = new tls_client_stats();
        set_app_stats (cs_grp_stats, cs_grp_label);

        std::vector<ev_sockstats*> *cs_grp_stats_arr 
            = new std::vector<ev_sockstats*> ();

        cs_grp_stats_arr->push_back (cs_grp_stats);
        cs_grp_stats_arr->push_back (m_app_stats);
        cs_grp_stats_arr->push_back (zone_app_stats);
        cs_grp_stats_arr->push_back (zone_sock_stats);

        tls_client_cs_grp* next_cs_grp 
            = new tls_client_cs_grp (cs_grp_cfg, cs_grp_stats_arr);

        next_cs_grp->m_ssl_ctx = SSL_CTX_new(TLS_client_method());

        int status = 0;
        if (next_cs_grp->m_version == sslv3) {
            status = SSL_CTX_set_min_proto_version (next_cs_grp->m_ssl_ctx, SSL3_VERSION);
            status = SSL_CTX_set_max_proto_version (next_cs_grp->m_ssl_ctx, SSL3_VERSION);
        } else if (next_cs_grp->m_version == tls1) {
            status = SSL_CTX_set_min_proto_version (next_cs_grp->m_ssl_ctx, TLS1_VERSION);
            status = SSL_CTX_set_max_proto_version (next_cs_grp->m_ssl_ctx, TLS1_VERSION);
        } else if (next_cs_grp->m_version == tls1_1) {
            status = SSL_CTX_set_min_proto_version (next_cs_grp->m_ssl_ctx, TLS1_1_VERSION);
            status = SSL_CTX_set_max_proto_version (next_cs_grp->m_ssl_ctx, TLS1_1_VERSION);
        } else if (next_cs_grp->m_version == tls1_2) {
            status = SSL_CTX_set_min_proto_version (next_cs_grp->m_ssl_ctx, TLS1_2_VERSION);
            status = SSL_CTX_set_max_proto_version (next_cs_grp->m_ssl_ctx, TLS1_2_VERSION);
        } else if (next_cs_grp->m_version == tls1_3) {
            status = SSL_CTX_set_min_proto_version (next_cs_grp->m_ssl_ctx, TLS1_3_VERSION);
            SSL_CTX_set_max_proto_version (next_cs_grp->m_ssl_ctx, TLS1_3_VERSION);
        } else {
            status = SSL_CTX_set_min_proto_version (next_cs_grp->m_ssl_ctx, SSL3_VERSION);
            status = SSL_CTX_set_max_proto_version (next_cs_grp->m_ssl_ctx, TLS1_3_VERSION);       
        }
        if (status){
            
        }

        if (next_cs_grp->m_version == tls_all) {
            next_cs_grp->m_cipher2 = cs_grp_cfg["cipher2"].get<std::string>().c_str();
            SSL_CTX_set_ciphersuites (next_cs_grp->m_ssl_ctx
                                        , next_cs_grp->m_cipher2.c_str());
            SSL_CTX_set_cipher_list (next_cs_grp->m_ssl_ctx
                                        , next_cs_grp->m_cipher.c_str());
        } else if (next_cs_grp->m_version == tls1_3) {
            SSL_CTX_set_ciphersuites (next_cs_grp->m_ssl_ctx
                                        , next_cs_grp->m_cipher.c_str());
        } else {
            SSL_CTX_set_cipher_list (next_cs_grp->m_ssl_ctx
                                        , next_cs_grp->m_cipher.c_str());
        }


        SSL_CTX_set_verify(next_cs_grp->m_ssl_ctx, SSL_VERIFY_NONE, 0);

        SSL_CTX_set_mode(next_cs_grp->m_ssl_ctx, SSL_MODE_ENABLE_PARTIAL_WRITE);

        SSL_CTX_set_session_cache_mode(next_cs_grp->m_ssl_ctx
                                            , SSL_SESS_CACHE_OFF);
        
        status = SSL_CTX_set1_groups_list(next_cs_grp->m_ssl_ctx
                                            , "P-521:P-384:P-256");

        SSL_CTX_set_dh_auto(next_cs_grp->m_ssl_ctx, 1);

        m_cs_groups.push_back (next_cs_grp);

        m_cs_group_count++;
    }
}

tls_client_app::~tls_client_app()
{

}

void tls_client_app::run_iter(bool tick_sec)
{
    if (m_cs_group_count == 0){
        return;
    }

    ev_app::run_iter (tick_sec);

    if (tick_sec)
    {
        m_app_stats->tick_sec();
    }

    for (int i=0; i < get_new_conn_count(); i++)
    {
        tls_client_cs_grp* cs_grp = m_cs_groups [m_cs_group_index];

        m_cs_group_index++;
        if (m_cs_group_index == m_cs_group_count)
        {
            m_cs_group_index = 0;
        }

        ev_sockaddrx* client_addr = cs_grp->get_next_clnt_addr ();
        if (client_addr)
        {
            tls_client_socket* client_socket = (tls_client_socket*) 
                                    new_tcp_connect (&client_addr->m_addr
                                                , cs_grp->get_server_addr()
                                                , cs_grp->m_stats_arr
                                                , client_addr->m_portq
                                                , &cs_grp->m_sock_opt);
            if (client_socket) 
            {
                m_client_curr_conn_count++;
                client_socket->m_app = this;
                client_socket->m_cs_grp = cs_grp;
            }
            else
            {
                printf ("new_tcp_connect fail!\n");
            }
        }
        else
        {
            printf ("get_next_clnt_addr fail!\n");
        }
    }
}

ev_socket* tls_client_app::alloc_socket()
{
    return new tls_client_socket();
}

void tls_client_app::free_socket(ev_socket* ev_sock)
{
    delete ev_sock;
}


void tls_client_socket::ssl_init ()
{
    m_ssl = SSL_new (m_cs_grp->m_ssl_ctx);
    if (m_ssl){
        set_as_ssl_client (m_ssl);
        SSL_set_tlsext_host_name (m_ssl, "www.google.com");
    } else {
        //stats
        abort ();
    }

    m_ssl_init = true;
}

void tls_client_socket::on_establish ()
{
}

void tls_client_socket::on_write ()
{
    if (m_bytes_written < m_cs_grp->m_cs_start_tls_len)
    {
        int next_chunk = m_cs_grp->m_cs_start_tls_len - m_bytes_written;
        int next_chunk_target = m_cs_grp->m_write_chunk;
        if (next_chunk_target == 0) {
            next_chunk_target = m_app->get_next_chunk_size ();
        }

        if ( next_chunk > next_chunk_target){
            next_chunk = next_chunk_target;
        }

        if ( next_chunk > m_cs_grp->m_write_buffer_len){
            next_chunk = m_cs_grp->m_write_buffer_len;
        }

        write_next_data (m_cs_grp->m_write_buffer, 0, next_chunk, true);
    }
    else
    {
        if (m_ssl_init) 
        {
            if (m_bytes_written < m_cs_grp->m_cs_data_len) {
                int next_chunk = m_cs_grp->m_cs_data_len - m_bytes_written;
                int next_chunk_target = m_cs_grp->m_write_chunk;
                if (next_chunk_target == 0) {
                    next_chunk_target = m_app->get_next_chunk_size ();
                }

                if ( next_chunk > next_chunk_target){
                    next_chunk = next_chunk_target;
                }

                if ( next_chunk > m_cs_grp->m_write_buffer_len){
                    next_chunk = m_cs_grp->m_write_buffer_len;
                }

                write_next_data (m_cs_grp->m_write_buffer, 0, next_chunk, true);

            } else {
                disable_wr_notification ();
            }
        }
        else
        {
            if ((m_bytes_written == m_cs_grp->m_cs_start_tls_len)
                    && (m_bytes_read == m_cs_grp->m_sc_start_tls_len))
            {
                ssl_init();
            }
        }
    }
}

void tls_client_socket::on_wstatus (int bytes_written, int write_status)
{
    if (write_status == WRITE_STATUS_NORMAL) 
    {
        m_bytes_written += bytes_written;        
        if (m_bytes_written == m_cs_grp->m_cs_data_len) 
        {
            if (m_cs_grp->m_close == close_reset){
                abort ();
            } else {
                switch (m_cs_grp->m_close_notify)
                {
                    case close_notify_no_send:
                        write_close ();
                        break;
                    case close_notify_send:
                        write_close (SSL_SEND_CLOSE_NOTIFY);
                        break;
                    case close_notify_send_recv:
                        write_close (SSL_SEND_RECEIVE_CLOSE_NOTIFY);
                        break;
                }
            }
        }       
    } 
    else 
    {
        abort ();
    }
}

void tls_client_socket::on_read ()
{
    if (m_bytes_read < m_cs_grp->m_sc_start_tls_len)
    {
        int next_chunk = m_cs_grp->m_sc_start_tls_len - m_bytes_read;
        if (next_chunk > m_cs_grp->m_read_buffer_len)
        {
            next_chunk = m_cs_grp->m_read_buffer_len;
        }
        read_next_data (m_cs_grp->m_read_buffer, 0, next_chunk, true);
    }
    else
    {
        if (m_ssl_init)
        {
            int next_chunk = m_cs_grp->m_read_buffer_len;
            read_next_data (m_cs_grp->m_read_buffer, 0, next_chunk, true);
        }
        else
        {
            if ((m_bytes_written == m_cs_grp->m_cs_start_tls_len)
                    && (m_bytes_read == m_cs_grp->m_sc_start_tls_len))
            {
                ssl_init();
            }  
        }
    }
}

void tls_client_socket::on_rstatus (int bytes_read, int read_status)
{    
    if (bytes_read == 0) 
    {
        if (read_status != READ_STATUS_TCP_CLOSE) {
            abort ();
        }
    } 
    else 
    {
        m_bytes_read += bytes_read;
    }
}

void tls_client_socket::on_finish ()
{
        if (m_ssl) {
            SSL_free (m_ssl);
            m_ssl = nullptr;
        }
}
