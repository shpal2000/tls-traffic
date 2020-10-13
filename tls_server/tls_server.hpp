#ifndef __TLS_SERVER_H__
#define __TLS_SERVER_H__

#include "app.hpp"

#define DEFAULT_WRITE_CHUNK 1200
#define DEFAULT_WRITE_BUFF_LEN 1000000
#define DEFAULT_READ_BUFF_LEN 1000000

class tls_server_srv_grp : public ev_app_srv_grp 
{
public:
    tls_server_srv_grp (json jcfg
                        , std::vector<ev_sockstats*> *stats_arr) 
                    
                    : ev_app_srv_grp (jcfg, stats_arr) 
    {
        m_cs_data_len = jcfg["cs_data_len"].get<int>();
        m_sc_data_len = jcfg["sc_data_len"].get<int>();
        m_cs_start_tls_len = jcfg["cs_start_tls_len"].get<int>();
        m_sc_start_tls_len = jcfg["sc_start_tls_len"].get<int>();
        m_srv_cert = jcfg["srv_cert"].get<std::string>().c_str();
        m_srv_key = jcfg["srv_key"].get<std::string>().c_str();
        m_cipher = jcfg["cipher"].get<std::string>().c_str();
        m_session_resumption = jcfg["session_resumption"].get<int>();

        const char* tls_version 
            = jcfg["tls_version"].get<std::string>().c_str();
        const char* close_type 
            = jcfg["close_type"].get<std::string>().c_str();
        const char* close_notify 
            = jcfg["close_notify"].get<std::string>().c_str();

        m_write_chunk = jcfg["write_chunk"].get<int>();
        if (m_write_chunk == 0){
            m_write_chunk = DEFAULT_WRITE_CHUNK;
        }

        m_write_buffer_len = jcfg["app_snd_buff"].get<uint32_t>();
        if (m_write_buffer_len == 0) {
            m_write_buffer_len = DEFAULT_WRITE_BUFF_LEN;
        }
        m_write_buffer = (char*) malloc (m_write_buffer_len);

        m_read_buffer_len = jcfg["app_rcv_buff"].get<uint32_t>();
        if (m_read_buffer_len == 0) {
            m_read_buffer_len = DEFAULT_READ_BUFF_LEN;
        }
        m_read_buffer = (char*) malloc (m_read_buffer_len);
       
        if (strcmp(close_type, "fin") == 0) {
            m_close = close_fin;
        } else if (strcmp(close_type, "reset") == 0) {
            m_close = close_reset;
        }else {
            m_close = close_fin;
        }

        if (strcmp(close_notify, "send") == 0) {
            m_close_notify = close_notify_send;
        } else if (strcmp(close_notify, "send_recv") == 0) {
            m_close_notify = close_notify_send_recv;
        } else if (strcmp(close_notify, "no_send") == 0)  {
            m_close_notify = close_notify_no_send;
        } else {
            m_close_notify = close_notify_send_recv;
        }

        if (strcmp(tls_version, "sslv3") == 0){
            m_version = sslv3;
        } else if (strcmp(tls_version, "tls1") == 0){
            m_version = tls1;
        } else if (strcmp(tls_version, "tls1_1") == 0){
            m_version = tls1_1;
        } else if (strcmp(tls_version, "tls1_2") == 0){
            m_version = tls1_2;
        } else if (strcmp(tls_version, "tls1_3") == 0){
            m_version = tls1_3;
        } else if (strcmp(tls_version, "tls_all") == 0){
            m_version = tls_all;
        } else {
            m_version = tls_all;
        }

        if (m_version == tls_all) {
            m_cipher2 = jcfg["cipher2"].get<std::string>().c_str();
        }
        else
        {
            m_cipher2 = "";
        }

        m_emulation_id = 0;
        m_next_cert_index = 1;
        m_max_cert_index = 1;
        
        try
        {
            m_emulation_id = jcfg["emulation_id"].get<int>();
            m_next_cert_index = jcfg["begin_cert_index"].get<int>();
            m_max_cert_index = jcfg["end_cert_index"].get<int>();
        }
        catch(const std::exception& e)
        {
        }
    }

    int m_cs_data_len;
    int m_sc_data_len;
    int m_cs_start_tls_len;
    int m_sc_start_tls_len;
    int m_write_chunk;
    char* m_read_buffer;
    char* m_write_buffer;
    int m_read_buffer_len;
    int m_write_buffer_len;

    int m_session_resumption;

    std::string m_srv_cert;
    std::string m_srv_key;
    std::string m_cipher;
    std::string m_cipher2;
    enum_close_type m_close;
    enum_close_notify m_close_notify;
    enum_tls_version m_version;

    int m_emulation_id;
    int m_next_cert_index;
    int m_max_cert_index;

    char m_next_cert [1024];
    char m_next_key [1024];

    SSL_CTX* m_ssl_ctx;

    SSL_CTX* create_ssl_ctx ()
    {
        SSL_CTX* ssl_ctx = SSL_CTX_new(TLS_server_method());

        if (ssl_ctx)
        {
            int status = 0;

            if (m_version == sslv3) {
                status = SSL_CTX_set_min_proto_version (ssl_ctx, SSL3_VERSION);
                status = SSL_CTX_set_max_proto_version (ssl_ctx, SSL3_VERSION);
            } else if (m_version == tls1) {
                status = SSL_CTX_set_min_proto_version (ssl_ctx, TLS1_VERSION);
                status = SSL_CTX_set_max_proto_version (ssl_ctx, TLS1_VERSION);
            } else if (m_version == tls1_1) {
                status = SSL_CTX_set_min_proto_version (ssl_ctx, TLS1_1_VERSION);
                status = SSL_CTX_set_max_proto_version (ssl_ctx, TLS1_1_VERSION);
            } else if (m_version == tls1_2) {
                status = SSL_CTX_set_min_proto_version (ssl_ctx, TLS1_2_VERSION);
                status = SSL_CTX_set_max_proto_version (ssl_ctx, TLS1_2_VERSION);
            } else if (m_version == tls1_3) {
                status = SSL_CTX_set_min_proto_version (ssl_ctx, TLS1_3_VERSION);
                SSL_CTX_set_max_proto_version (ssl_ctx, TLS1_3_VERSION);
            } else {
                status = SSL_CTX_set_min_proto_version (ssl_ctx
                                                        , SSL3_VERSION);
                status = SSL_CTX_set_max_proto_version (ssl_ctx
                                                        , TLS1_3_VERSION);           
            }
            if (status){

            }

            if (m_version == tls_all) {
                SSL_CTX_set_ciphersuites (ssl_ctx, m_cipher2.c_str());
                SSL_CTX_set_cipher_list (ssl_ctx, m_cipher.c_str());
            } else if (m_version == tls1_3) {
                SSL_CTX_set_ciphersuites (ssl_ctx, m_cipher.c_str());
            } else {
                SSL_CTX_set_cipher_list (ssl_ctx, m_cipher.c_str());
            }

            SSL_CTX_set_mode(ssl_ctx, SSL_MODE_ENABLE_PARTIAL_WRITE);


            if (m_session_resumption){
                SSL_CTX_set_session_cache_mode(ssl_ctx
                                                , SSL_SESS_CACHE_SERVER);
            } else {
                SSL_CTX_set_session_cache_mode(ssl_ctx
                                                , SSL_SESS_CACHE_OFF);
            }

            SSL_CTX_set_session_id_context(ssl_ctx
                                                , (unsigned char*)this
                                                , sizeof(void*)); 

            SSL_CTX_set1_groups_list(ssl_ctx, "P-521:P-384:P-256");

            SSL_CTX_set_dh_auto(ssl_ctx, 1);

            const char* server_cert;
            const char* server_key;

            if (m_emulation_id == 0){
                server_cert = m_srv_cert.c_str();
                server_key = m_srv_key.c_str();
            }else{
                sprintf (m_next_cert, "/rundir/certs/server%d.cert", m_next_cert_index);
                sprintf (m_next_key, "/rundir/certs/server%d.key", m_next_cert_index);
                server_cert = m_next_cert;
                server_key = m_next_key;
                m_next_cert_index++;
                if (m_next_cert_index > m_max_cert_index){
                    m_next_cert_index = 1;
                }
            }

            std::ifstream f(server_cert);
            std::ostringstream ss;
            std::string str;
            ss << f.rdbuf();
            str = ss.str();

            BIO *bio = NULL;
            BIO *kbio = NULL;
            X509 *cert = NULL;
            bio = BIO_new_mem_buf((char *)str.c_str(), -1);
            cert = PEM_read_bio_X509(bio, NULL, 0, NULL);
            SSL_CTX_use_certificate (ssl_ctx, cert);

            std::ifstream f2(server_key);
            std::ostringstream ss2;
            std::string str2;
            ss2 << f2.rdbuf();
            str2 = ss2.str();
            kbio = BIO_new_mem_buf(str2.c_str(), -1);
            EVP_PKEY *key = NULL;
            key = PEM_read_bio_PrivateKey(kbio, NULL, 0, NULL);
            SSL_CTX_use_PrivateKey(ssl_ctx, key);

            BIO_free(bio);
            BIO_free(kbio);
            EVP_PKEY_free(key);
            X509_free(cert);
        }

        return ssl_ctx;
    }
};

struct tls_server_stats_data : app_stats
{
    uint64_t tls_server_stats_1;
    uint64_t tls_server_stats_100;

    virtual void dump_json (json &j)
    {
        app_stats::dump_json (j);
        
        j["tls_server_stats_1"] = tls_server_stats_1;
        j["tls_server_stats_100"] = tls_server_stats_100;
    }

    virtual ~tls_server_stats_data() {};
};

struct tls_server_stats : tls_server_stats_data
{
    tls_server_stats () : tls_server_stats_data () {}
};
class tls_server_app : public app
{
public:
    tls_server_app(json app_json
                    , tls_server_stats* all_app_stats
                    , ev_sockstats* all_ev_app_stats);

    ~tls_server_app();

    void run_iter(bool tick_sec);

    ev_socket* alloc_socket();
    void free_socket(ev_socket* ev_sock);

public:
    std::vector<tls_server_srv_grp*> m_srv_groups;
};

class tls_server_socket : public ev_socket
{
public:
    tls_server_socket()
    {
        m_bytes_written = 0;
        m_bytes_read = 0;
        m_ssl = nullptr;
        m_ssl_ctx = nullptr;
        m_ssl_init = false;
    };

    virtual ~tls_server_socket()
    {

    };

    void ssl_init ();

    void on_establish ();
    void on_write ();
    void on_wstatus (int bytes_written, int write_status);
    void on_read ();
    void on_rstatus (int bytes_read, int read_status);
    void on_finish ();

public:
    tls_server_srv_grp* m_srv_grp;
    tls_server_app* m_app;
    tls_server_socket* m_lsock;
    SSL* m_ssl;
    int m_bytes_written;
    int m_bytes_read;

private:
    SSL_CTX* m_ssl_ctx;
    bool m_ssl_init;
};

#define inc_tls_server_stats(__stat_name) \
{ \
    inc_app_stats(ev_sock,tls_server_stats,__stat_name); \
}

#endif