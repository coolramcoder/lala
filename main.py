import wave
import time
import socket
import random
import pyaudio
import datetime
from s import ServerNetwork
from c import ClientNetwork
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen


class Welcome(Screen):
    """This class inherits kivy's screen class(for multiple screen) , display's welcome message
       with licence info and a continue button which switches screen to /central screen """

    # initialising Screen class with super method
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # welcome text label
        welcome_label = Label(
            text="Welcome to AudioMerge\na TetraPlex Product\n\nlicensed under GPL3 Copyright TetraPlex 2023",
            font_size='35sp',
            halign='center'
        )

        # continue button
        start_button = Button(
            text='continue',
            size_hint=(None, None),
            size=(200, 50),  # Set button size
            pos_hint={'center_x': 0.5, 'top': 0.2},
            on_release=self.switch_to_options
        )

        # adding widgets to welcome window
        self.add_widget(welcome_label)
        self.add_widget(start_button)

    # when button is pressed, current screen is changed to root/main window
    def switch_to_options(self, button_instance):
        self.manager.current = "client_server_option"


class ClientServerOption(Screen):
    """ This class inherits kivy's screen class(for multiple screen) , give user option to choose to be central or
    satellite node"""

    # initialising Screen class with super method
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # AnchorLayout for label
        self.label_layout = AnchorLayout(anchor_x='center', anchor_y='top', padding=10)
        self.label = Label(text="choose which node this device should run", font_size='35sp', size_hint_y=None)

        # GridLayout for buttons
        self.button_layout = GridLayout(cols=2, spacing=10, padding=100, row_force_default=True, row_default_height=50)
        self.central_button = Button(text="central", size_hint=(7, 2), size=(200, 50),
                                     on_press=self.switch_to_central)
        self.button = Button(text="satellite", size_hint=(7, 2), size=(200, 50),
                              on_press=self.switch_to_satellite)

        # adding widgets to screen
        self.label_layout.add_widget(self.label)
        self.button_layout.add_widget(self.central_button)
        self.button_layout.add_widget(self.button)
        self.add_widget(self.label_layout)
        self.add_widget(self.button_layout)

    # methods to switch screen to central
    def switch_to_central(self, button_instance):
        self.manager.current = "server"

    # methods to switch screen to 
    def switch_to_satellite(self, button_instance):
        self.manager.current = "client"

class Record():
    """
    handles recording, saving of audio files and changes recording flag
    """
    def start_recording(self, instance):
        """
        Handles GUI changes and audio recording initiation.
        It opens an audio stream and starts recording using the callback method.

        also checks whether pyaudio object has been successfully initialized or not and if not
        then raises an OS error
        """
        try:
            # pyaudio object
            self.audio = pyaudio.PyAudio()
            # audio stream, "input=true" => record from default microphone
            self.stream = self.audio.open(format=pyaudio.paInt16,
                                          channels=1,
                                          rate=44100,
                                          input=True,
                                          frames_per_buffer=1024,
                                          stream_callback=self.callback)
            
        except OSError:
            raise OSError("can't access microphone")

        else:
            # audio streams are stored as a list in frames object
            self.frames = []
            self.stream.start_stream()

    def callback(self, in_data, frame_count, time_info, status):
        """ A callback function for the audio stream that appends recorded audio frames to a list
            takes in new audio data and appends it to frames object """

        # appending "in_data" to self.frame and continuing to record audio stream
        self.frames.append(in_data)
        return (None, pyaudio.paContinue)

    def stop_recording(self, instance):
        """ stops & terminates recording and ensures streaming and use of resources has stopped """

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.save_recorded_audio()

    def save_recorded_audio(self):
        """ Saves the recorded audio frames to a WAV file using the
        current date and time as part of the filename """
        date = datetime.datetime.now().strftime("%y_%m_%d")
        time = datetime.datetime.now().strftime("%H_%M_%S")

        # formatting file name
        self.recorded_filename = f"audiomerge{date}at{time}.wav"

        # checking whether audio data exists
        if self.frames:
            with wave.open(self.recorded_filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.frames))
        else:
            raise ValueError("no audio data available to write")



class Server(Record, Screen, ServerNetwork):
    # initializing Screen class with super() method
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

    def central_rec_start(self,instance):
        self.start_recording(instance)
        self.server_network.msg_frm_server_to_start()
        self.recording_status.text = "recording...."
        self.Record_button.disabled = True
        self.Stop_button.disabled = False
        

    def central_rec_stop(self,instance):
        self.stop_recording(instance)
        self.server_network.msg_frm_server_to_stop()
        self.Record_button.disabled = False
        self.Stop_button.disabled = True
        self.recording_status.text = "Press record to start recording"

    def on_enter(self):
        """ this function is called when server screen is loaded, it starts server thread"""

        ''' screen is updated every second to update number of connected clients'''
        
        server_network = ServerNetwork()
        server_network.start_server()

        # grid layout
        self.label_layout = AnchorLayout(anchor_x='center', anchor_y='top', padding=10)
        self.Label = Label(text="central", font_size='35sp', size_hint_y=None)

        self.grid_layout = GridLayout(cols=2, spacing=10, padding=100, row_force_default=True, row_default_height=50)

        self.ip_address_label = Label(text="IP Address: ", font_size='30sp')
        self.ip_address = Label(text=str(server_network.host), font_size='30sp')

        self.port_label = Label(text="Port: ", font_size='30sp')
        self.port = Label(text=str(server_network.port), font_size='30sp')

        self.client_number_label = Label(text="active clinets: ", font_size='30sp')
        self.client_number = Label(text=str(server_network.active_clients), font_size='30sp')

        self.recording_status = Label(text= "Press record to start recording")

        self.Record_button = Button(text="Record",
                                    size_hint=(7, 2),
                                    size=(200, 50), on_press=self.central_rec_start)

        self.Stop_button = Button(text="Stop",
                                  size_hint=(7, 2),
                                  size=(200, 50), on_press=self.central_rec_stop)
        
        self.Stop_button.disabled = True

        # adding widgets to server window
        self.label_layout.add_widget(self.Label)
        self.grid_layout.add_widget(self.ip_address_label)
        self.grid_layout.add_widget(self.ip_address)
        self.grid_layout.add_widget(self.port_label)
        self.grid_layout.add_widget(self.port)
        self.grid_layout.add_widget(self.client_number_label)
        self.grid_layout.add_widget(self.client_number)
        self.label_layout.add_widget(self.recording_status)
        self.grid_layout.add_widget(self.Record_button)
        self.grid_layout.add_widget(self.Stop_button)

        self.add_widget(self.label_layout)
        self.add_widget(self.grid_layout)




    def on_leave(self, serverthread):
        """ this function is called when server screen is left, it stops server thread"""
        

        # Bind the function to the TextInput's touch event
           

                
class Client(Screen):
    """ This class inherits kivy's screen class(for multiple screen), and used to connect to central node"""
    ip,port = "",0
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #  node
        self.label_layout = AnchorLayout(anchor_x='center', anchor_y='top', padding=10)
        self.label = Label(text=" node", font_size='35sp', size_hint_y=None)

        # input layout
        self.input_layout = GridLayout(cols=2, spacing=30, padding=100, row_force_default=True, row_default_height=50)
        self.ip_address_lable = Label(text="IP Address :", font_size='30sp')
        self.ip_address = TextInput(font_size='20sp', multiline=False, cursor_blink=True)

        self.port_label = Label(text="Port :", font_size='30sp')
        self.port = TextInput(font_size='20sp', multiline=False, cursor_blink=True)

        # continue button
        self.continue_button_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', padding=40)
        self.continue_button = Button(text="continue", size_hint=(None, None), size=(200, 50),
                                      on_press=self.switch_to_main)

        # adding widgets to client window
        self.label_layout.add_widget(self.label)
        self.input_layout.add_widget(self.ip_address_lable)
        self.input_layout.add_widget(self.ip_address)
        self.input_layout.add_widget(self.port_label)
        self.input_layout.add_widget(self.port)
        self.continue_button_layout.add_widget(self.continue_button)

        # adding layouts to client window
        self.add_widget(self.label_layout)
        self.add_widget(self.input_layout)
        self.add_widget(self.continue_button_layout)

    def switch_to_main(self, button_instance):
        Client.ip = str(self.ip_address.text)
        Client.port = int(self.port.text)
        self.manager.current = "main"

class RecordScreen(Screen,Record,ClientNetwork):
    """ This class represents our root window, which contains main functionality of app
    i.e, audio recording """
    # def on_enter(self, *args):
    #     Clock.schedule_interval(self.check_state,1)
        
    record = Record()
    
    def on_enter(self, *args):
        client_object = ClientNetwork()
        ip,port = Client.ip,Client.port
        print("@"*50)
        print(f"bhai text mai ye hai {Client.ip}:{Client.port} aur type hai {type(Client.ip)};{type(Client.port)}")
        print("@"*50)

        client_object.connect(host=ip, port=port)
         

    # initializing Screen class with super() method
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # creating a box label_layout(child widgets on top of main root window)
        self.label_layout = AnchorLayout(anchor_x='center', anchor_y='top', padding=10)
        self.label = Label(text="Press 'Record' to start recording", font_size='35sp', size_hint_y=None)

        # record_button, which triggers "start_recording" function on press, enabled defaulter
        self.button_layout = GridLayout(cols=2, spacing=10, padding=100, row_force_default=True, row_default_height=50)
        self.record_button = Button(text="Record",
                                     size_hint=(7, 2),
                                     size=(200, 50), on_press=self.change_widget_onstart)

        # stop_button, which triggers "stop_recording" function on press, disabled by-default
        self.stop_button = Button(text="Stop",
                                   size_hint=(7, 2),
                                   size=(200, 50), on_press=self.change_widget_onstop)
        self.stop_button.disabled = True

        # adding widgets to boxlayout and returning label_layout
        self.label_layout.add_widget(self.label)
        self.button_layout.add_widget(self.record_button)
        self.button_layout.add_widget(self.stop_button)
        self.add_widget(self.label_layout)
        self.add_widget(self.button_layout)
    
    def change_widget_onstart(self, instance):
        self.label.text = "Recording..."
        RecordScreen.record.start_recording(instance)
        self.record_button.disabled = True
        self.stop_button.disabled = False
        self.send_to_server_start()
                
    def change_widget_onstop(self, instance):
        # when this functon is called:
        # lable changes to "recording stopped."
        # start_record button enables for another recording
        # stop_record button disables until new recording begins
        self.label.text = "Recording stopped"
        RecordScreen.record.stop_recording(instance)
        self.record_button.disabled = False
        self.stop_button.disabled = True
        self.send_to_server_stop()
        
    def check_state(self,dt):
        if ClientNetwork.msg == True:
            self.change_widget_onstart(instance=None)
        elif ClientNetwork.msg == False:
            self.change_widget_onstop(instance=None)
        
class AudiomergeApp(App):
    """ this class inherits App class of Kivy,"build" method creates and returns an 
        instance of the ScreenManager that manages different screens of the app"""

    def build(self):
        # creating an instance of Screen manager class
        sm = ScreenManager()

        # adding Screen to Screen manager
        sm.add_widget(Welcome(name="welcome"))
        sm.add_widget(ClientServerOption(name="client_server_option"))
        sm.add_widget(Server(name="server"))  # Make sure "server" is added before "main"
        sm.add_widget(Client(name="client"))
        sm.add_widget(RecordScreen(name="main"))
        return sm

if __name__ == '__main__':
    AudiomergeApp().run()