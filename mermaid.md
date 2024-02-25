classDiagram
    class App{
    }

    class AudiomergeApp{
        + ScreenManager: object
        Build()
         object.add_widget(widget) screens
    }
    class Welcome{
        - Welcome_label
        - continue_button
        switch_to_options()
    }
    class ClientServerOption{
         Anchor layout
        - option label
        - central button 
        - setallite/node button
        switch_to_central()
        switch_to_satellite()
    }

    namespace server thread{
    class Server{
        Grid layout
        - label: central
        + ipaddres 
        + port
        on_enter()
        update()
        on_leave(server thread)
    }
}

    class server_module{
        get_ipaddress()
        get_port()
        bind(ipaddres,port) server socket
        listen(server socket)
        accept_connections(server socket)
        accept_connections(server socket) Client
        handle_clients(Client)
    }

    class shared_values{
        + number_of_cleints
        + clients[]
        + recording_flag
        + increment_client()
        + show_clients()
        + add_client()

    }

    class Client{
        connect(ipaddres,port)
        send_flag(client)
        reciev_flag(client)
    }
    class Record{
        - Box layout
        - label
        - frames[]
        start_recording()
        stop_recording()
        save_recorded_audio(frames)

    }


    App <|.. AudiomergeApp : inheriting Kivy's App class
    AudiomergeApp <|-- Welcome : inheriting Screen class
    AudiomergeApp <|-- ClientServerOption : inheriting Screen class
    AudiomergeApp <|-- Record : inheriting Screen class
    AudiomergeApp <|-- Client : inheriting Screen class
    AudiomergeApp <|-- Server : inheriting Screen class
    Server ..> shared_values : dependency
    Server ..> server_module : dependency
    Client ..> shared_values : dependency
    




