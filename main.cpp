#include <stdio.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <signal.h>
#include <chrono>

#include "./tls_server/tls_server.hpp"
#include "./tls_client/tls_client.hpp"
#include "./tcp_proxy/tcp_proxy.hpp"

#define RUN_DIR_PATH "/rundir/"

app_stats* zone_ev_sockstats = nullptr;
tls_server_stats* zone_tls_server_stats = nullptr;
tls_client_stats* zone_tls_client_stats = nullptr;
tcp_proxy_stats* zone_tcp_proxy_stats = nullptr;

static void system_cmd (const char* label, const char* cmd_str)
{
    printf ("%s ---- %s\n\n", label, cmd_str);
    fflush (NULL);
    system (cmd_str);
}

static void dump_stats (const char* out_file, app_stats* stats) 
{
    json j;
    
    stats->dump_json(j);

    std::ofstream stats_stream(out_file);
    stats_stream << j << std::endl;
}

static void config_zone (json cfg_json
                            , int z_index)
{
    auto zone_cmds = cfg_json["zones"][z_index]["zone_cmds"];

    //run all zone commands
    for (auto cmd_it = zone_cmds.begin(); cmd_it != zone_cmds.end(); ++cmd_it) {
        auto cmd = cmd_it.value().get<std::string>();
        system_cmd ("zone_cmd", cmd.c_str());
    }
}

static std::vector<app*>* create_app_list (json cfg_json, int z_index)
{
    std::vector<app*> *app_list = nullptr;

    auto a_list = cfg_json["zones"][z_index]["app_list"];
    for (auto a_it = a_list.begin(); a_it != a_list.end(); ++a_it)
    {
        auto app_json = a_it.value ();

        int app_enable = app_json["enable"].get<int>();
        if (app_enable ==0){
            continue;
        }

        if (zone_ev_sockstats == nullptr)
        {
            zone_ev_sockstats = new app_stats();
        }

        app* next_app = nullptr;
        const char* app_type = app_json["app_type"].get<std::string>().c_str();
        const char* app_label = app_json["app_label"].get<std::string>().c_str();

        if ( strcmp("tls_server", app_type) == 0 )
        {
            if (zone_tls_server_stats == nullptr)
            {
                zone_tls_server_stats = new tls_server_stats ();
            }

            next_app = new tls_server_app (app_json
                                            , zone_tls_server_stats
                                            , zone_ev_sockstats);

        }
        else if ( strcmp("tls_client", app_type) == 0 )
        {
            if (zone_tls_client_stats == nullptr)
            {
                zone_tls_client_stats = new tls_client_stats ();
            }
            
            next_app = new tls_client_app (app_json
                                            , zone_tls_client_stats
                                            , zone_ev_sockstats);
        }
        else if ( strcmp("tcp_proxy", app_type) == 0 )
        {
            if (zone_tcp_proxy_stats == nullptr)
            {
                zone_tcp_proxy_stats = new tcp_proxy_stats ();
            }
            
            next_app = new tcp_proxy_app (app_json
                                            , zone_tcp_proxy_stats
                                            , zone_ev_sockstats);
        }

        if (next_app)
        {
            next_app->set_app_type (app_type);
            next_app->set_app_label (app_label);

            if (app_list == nullptr)
            {
                app_list = new std::vector<app*>;
            }

            app_list->push_back (next_app);
        }
        else
        {
            printf ("unknown app_type %s\n", app_type);
            exit (-1);
        }
    }

    return app_list;
}

int main(int /*argc*/, char **argv) 
{
    char cfg_dir [512]; // not needed
    char cfg_file [1024]; //make it cmd args
    char result_dir [1024]; //make it cmd args

    char stats_file [1024];

    char* mode = argv[1];
    char* cfg_name = argv[2];

    sprintf (cfg_dir, "%straffic/%s/", RUN_DIR_PATH, cfg_name);
    sprintf (cfg_file, "%s%s", cfg_dir, "config.json");

    std::ifstream cfg_stream(cfg_file);
    json cfg_json = json::parse(cfg_stream);

    char* run_tag = argv[3];
    int z_index = atoi (argv[4]);
    char* config_zone_flag = argv[5];
    
    auto zone_label 
        = cfg_json["zones"][z_index]["zone_label"].get<std::string>();

    sprintf (result_dir, "%straffic/%s/%s/%s/", RUN_DIR_PATH, cfg_name
                                                , "results", run_tag);
    
    if ( strcmp(config_zone_flag, "config_zone") == 0 )
    {
        config_zone (cfg_json, z_index);
    }

    signal(SIGPIPE, SIG_IGN);

    OpenSSL_add_ssl_algorithms ();
    SSL_load_error_strings ();

    std::vector<app*> *app_list = create_app_list (cfg_json, z_index);

    if ( app_list )
    {
        std::chrono::time_point<std::chrono::system_clock> start, end;
        start = std::chrono::system_clock::now();
        int tick_5sec = 0;
        bool is_tick_sec = false;
        while (1)
        {
            std::this_thread::sleep_for(std::chrono::microseconds(1));
            end = std::chrono::system_clock::now();
            auto ms_elapsed 
                = std::chrono::duration_cast<std::chrono::milliseconds>
                (end-start);

            if (ms_elapsed.count() >= 1000)
            {
                start = end;
                is_tick_sec = true;
                tick_5sec++;
            }

            for (app* app_ptr : *app_list)
            {
                app_ptr->run_iter (is_tick_sec);
            }

            if (is_tick_sec) 
            {
                zone_ev_sockstats->tick_sec ();

                is_tick_sec = false;
            }

            if (tick_5sec == 5)
            {
                tick_5sec = 0;

                sprintf (stats_file,
                        "%s%s/"
                        "ev_sockstats.json",
                        result_dir, zone_label.c_str());
                dump_stats (stats_file, zone_ev_sockstats);

                if (zone_tls_server_stats)
                {
                    sprintf (stats_file,
                            "%s%s/"
                            "tls_server_stats.json",
                            result_dir, zone_label.c_str());
                    dump_stats (stats_file, zone_tls_server_stats);
                }

                if (zone_tls_client_stats)
                {
                    sprintf (stats_file,
                            "%s%s/"
                            "tls_client_stats.json",
                            result_dir, zone_label.c_str());
                    dump_stats (stats_file, zone_tls_client_stats);
                }

                for (app* app_ptr : *app_list)
                {
                    sprintf (stats_file,
                        "%s%s/"
                        "%s/%s_stats.json",
                        result_dir, zone_label.c_str(),
                        app_ptr->get_app_label(), app_ptr->get_app_type());
                    dump_stats (stats_file
                                , (app_stats*)app_ptr->get_app_stats());

                    ev_stats_map* app_stats_map 
                        = app_ptr->get_app_stats_map ();
                    for (auto it=app_stats_map->begin(); 
                            it!=app_stats_map->end(); ++it)
                    {
                        sprintf (stats_file,
                        "%s%s/"
                        "%s/%s/"
                        "%s_stats.json",
                        result_dir, zone_label.c_str(),
                        app_ptr->get_app_label(), it->first.c_str(),
                        app_ptr->get_app_type());
                        dump_stats (stats_file, (app_stats*)it->second);  
                    }
                }
            }
        }

        for (std::string line; std::getline(std::cin, line);) 
        {
            std::cout << line << std::endl;
        }
    }
    else
    {
        printf ("no apps!\n");
        exit (-1);
    }

    return 0;
}


