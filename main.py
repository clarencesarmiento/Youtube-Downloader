import customtkinter as ctk
from tkinter import filedialog
from tkinter import *
from PIL import Image
from pytube import YouTube
import pytube.exceptions
import os
import threading
from tkextrafont import Font
import sys
import json

from backend.backend import video_filter, audio_filter, get_audio_stream
from middleware.youtube_link import YouTubeLink

ctk.set_appearance_mode('light')
ctk.set_default_color_theme('blue')

# Set Application Width and Height
appWidth, appheight = 800, 500


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def load_json():
    with open('design_elements.json') as f:
        design_data = json.load(f)

    design_data['fonts']['title'] = tuple(design_data['fonts']['title'])
    design_data['fonts']['paragraph'] = tuple(design_data['fonts']['paragraph'])
    design_data['fonts']['small'] = tuple(design_data['fonts']['small'])

    return design_data['colors'], design_data['fonts'], design_data['images']


def create_frame(master):
    frame = ctk.CTkFrame(master, fg_color=(colors['neutral_200'], colors['neutral_400']),
                         corner_radius=0)
    frame.columnconfigure(0, weight=1)
    return frame


def create_entry(master, text, icon):
    frame = ctk.CTkFrame(master, fg_color='transparent', border_width=2, border_color=colors['neutral_300'],
                         corner_radius=8, )
    frame.columnconfigure(0, weight=1)

    entry = ctk.CTkEntry(frame, placeholder_text=text, text_color=(colors['neutral_500'], colors['neutral_100']),
                         font=fonts['paragraph'], fg_color='transparent', border_width=0, )
    entry.grid(row=0, column=0, padx=(10, 0), pady=10, sticky='nsew')

    icon_label = ctk.CTkLabel(frame, text='', image=icon, cursor='hand2')
    icon_label.grid(row=0, column=1, padx=10, pady=10, )

    return frame


def create_error_label(master,):
    label = ctk.CTkLabel(master, text='', font=fonts['small'])
    return label


def create_radiobutton(master, text, var, val, command):
    radio_button = ctk.CTkRadioButton(master, text=text, text_color=(colors['neutral_500'], colors['neutral_100']),
                                      font=fonts['paragraph'], radiobutton_width=20, radiobutton_height=20,
                                      border_color=colors['neutral_400'],
                                      border_width_unchecked=2, border_width_checked=5,
                                      fg_color=(colors['accent_0'], colors['accent_1']),
                                      hover_color=(colors['accent_0'], colors['accent_1']),
                                      variable=var, value=val, command=command)
    return radio_button


def create_optionmenu(master, val, var, command, ):
    option_menu = ctk.CTkOptionMenu(master, values=val, variable=var, height=40,
                                    text_color=(colors['neutral_500'], colors['neutral_100']),
                                    font=fonts['paragraph'], fg_color=(colors['neutral_200'], colors['neutral_400']),
                                    button_color=colors['accent_0'], button_hover_color=colors['accent_1'],
                                    dropdown_font=fonts['paragraph'],
                                    dropdown_text_color=(colors['neutral_500'], colors['neutral_100']),
                                    dropdown_fg_color=(colors['neutral_200'], colors['neutral_400']),
                                    dropdown_hover_color=(colors['accent_0'], colors['accent_1']),
                                    anchor='center',
                                    command=command)
    return option_menu


def create_button(master, text, icon, command):
    button = ctk.CTkButton(master, text=text, text_color=colors['neutral_100'], font=fonts['paragraph'],
                           fg_color=colors['accent_0'], hover_color=colors['accent_1'], image=icon,
                           compound='left', anchor='center', cursor='hand2', height=40, command=command)
    return button


def create_progress_bar(master):
    frame = ctk.CTkFrame(master, fg_color='transparent')
    frame.columnconfigure(0, weight=1)

    download_status = ctk.CTkLabel(frame, text='', font=fonts['small'],
                                   text_color=(colors['success_600'], colors['success_400']))
    download_status.grid(row=0, column=0, sticky='w')

    download_progress = ctk.CTkLabel(frame, text='0%', font=fonts['paragraph'],
                                     text_color=(colors['neutral_500'], colors['neutral_100']))
    download_progress.grid(row=0, column=0, sticky='e')

    progress_bar = ctk.CTkProgressBar(frame, fg_color=colors['neutral_300'], progress_color=colors['accent_0'],
                                      orientation='horizontal', height=10)
    progress_bar.set(0)
    progress_bar.grid(row=1, column=0, sticky='ew')

    download_title = ctk.CTkLabel(frame, text='', font=fonts['paragraph'],
                                  text_color=(colors['neutral_500'], colors['neutral_100']), )
    download_title.grid(row=2, column=0, sticky='w')

    return frame


# Load Design Elements from json file
colors, fonts, images = load_json()

error_text_color = (colors['danger_600'], colors['danger_400'])
warning_text_color = (colors['warning_600'], colors['warning_400'])
success_text_color = (colors['success_600'], colors['success_400'])

# Load and Set images
mode_icon = ctk.CTkImage(light_image=Image.open(resource_path(images['moon_icon'])),
                         dark_image=Image.open(resource_path(images['sun_icon'])),
                         size=(20, 20))
paste_icon = ctk.CTkImage(light_image=Image.open(resource_path(images['paste_icon_light'])),
                          dark_image=Image.open(resource_path(images['paste_icon_dark'])),
                          size=(25, 25))
download_icon = ctk.CTkImage(Image.open(resource_path('Assets/download-arrow.png')),
                             size=(20, 15))


class App(ctk.CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set Font
        Font(file=resource_path('Fonts/Inter-VariableFont_slnt,wght.ttf'), family='Inter')

        # Place App in Center of Screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - appWidth) // 2
        y = (screen_height - appheight) // 2

        # Create Window
        self.geometry(f'{appWidth}x{appheight}+{x}+{y}')
        self.resizable(False, False)
        self.title('YouTube Downloader')
        self.iconbitmap('Assets/play.ico')
        self.configure(fg_color=(colors['neutral_100'], colors['neutral_500']))

        self.current_mode = 'light'
        self.radio_var = IntVar(value=0)
        self.option_menu_var = StringVar(value='')
        self.youtube_link = YouTubeLink()

        # Configure App grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(7, weight=1)

        self.top_frame = create_frame(self)
        self.top_frame.grid(row=0, column=0, sticky='nsew')

        self.title_label = ctk.CTkLabel(self.top_frame, text='YOUTUBE VIDEO & AUDIO DOWNLOADER',
                                        text_color=(colors['neutral_500'], colors['neutral_100']),
                                        font=fonts['title'])
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky='w')

        self.mode_icon = ctk.CTkLabel(self.top_frame, text='', image=mode_icon, cursor='hand2')
        self.mode_icon.grid(row=0, column=0, padx=20, pady=20, sticky='e')

        self.link_entry = create_entry(self, text='Paste YouTube Link here', icon=paste_icon)
        self.link_entry.grid(row=1, column=0, padx=150, pady=(70, 0), sticky='nsew')

        self.error_label = create_error_label(self,)
        self.error_label.grid(row=2, column=0, padx=155, sticky='w')

        self.widget_frame = ctk.CTkFrame(self, fg_color=(colors['neutral_100'], colors['neutral_500']))
        self.widget_frame.grid(row=3, column=0, padx=150, sticky='ew')
        self.widget_frame.columnconfigure(2, weight=1)

        self.video_radiobutton = create_radiobutton(self.widget_frame, text='Video', var=self.radio_var, val=1,
                                                    command=self.radio_button_callback)
        self.video_radiobutton.grid(row=0, column=0, padx=10)

        self.audio_radiobutton = create_radiobutton(self.widget_frame, text='Audio', var=self.radio_var, val=2,
                                                    command=self.radio_button_callback)
        self.audio_radiobutton.grid(row=0, column=1, padx=10)

        self.video_radiobutton.configure(state='disabled')
        self.audio_radiobutton.configure(state='disabled')

        self.option_menu = create_optionmenu(self.widget_frame, val=[], var=self.option_menu_var,
                                             command=None)
        self.option_menu.grid(row=0, column=2, sticky='ew')

        self.download_button = create_button(self, text='Download', icon=download_icon, command=self.on_download)
        self.download_button.grid(row=4, column=0, padx=150, pady=(20, 0), sticky='e')

        self.download_button.configure(state='disabled')

        self.download_error_label = create_error_label(self,)
        self.download_error_label.grid(row=5, column=0, padx=155, sticky='e')

        self.progress_frame = create_progress_bar(self)
        self.progress_frame.grid(row=6, column=0, padx=150, sticky='ew')

        self.bottom_frame = create_frame(self, )
        self.bottom_frame.grid(row=8, column=0, sticky='ew')

        self.bottom_label1 = ctk.CTkLabel(self.bottom_frame, text='Designed and Developed by clarencesarmiento',
                                          text_color=(colors['neutral_500'], colors['neutral_100']),
                                          font=fonts['small'])
        self.bottom_label1.grid(row=0, column=0, padx=20, pady=5, sticky='w')

        self.bottom_label2 = ctk.CTkLabel(self.bottom_frame, text='Powered by pytube',
                                          text_color=(colors['neutral_500'], colors['neutral_100']),
                                          font=fonts['small'])
        self.bottom_label2.grid(row=0, column=0, padx=20, pady=5, sticky='e')

        # Event Binding
        self.mode_icon.bind('<Button-1>', lambda event: self.change_mode())
        self.link_entry.winfo_children()[0].bind('<KeyRelease>', lambda event: self.youtube_link_is_valid())
        self.link_entry.winfo_children()[1].bind('<Button-1>', lambda event: self.on_paste())

    def change_mode(self):
        if self.current_mode == 'light':
            ctk.set_appearance_mode('dark')
            self.current_mode = 'dark'
        else:
            ctk.set_appearance_mode('light')
            self.current_mode = 'light'

    def youtube_link_is_valid(self):
        try:
            self.youtube_link.youtube_link = self.link_entry.winfo_children()[0].get().strip()
            YouTube(self.youtube_link.youtube_link)
            self.error_label.configure(text='Success: Link valid.', text_color=success_text_color)
            self.link_entry.configure(border_color=(colors['success_600'], colors['success_400']))
            self.video_radiobutton.configure(state='normal')
            self.audio_radiobutton.configure(state='normal')
            self.download_button.configure(state='normal')
            return True
        except ValueError as e:
            self.error_label.configure(text=e, text_color=warning_text_color)
            self.link_entry.configure(border_color=(colors['warning_600'], colors['warning_400']))
            self.video_radiobutton.configure(state='disabled')
            self.audio_radiobutton.configure(state='disabled')
            self.download_button.configure(state='disabled')
            return False
        except pytube.exceptions.ExtractError:
            self.error_label.configure(text='Error: Invalid YouTube Link.', text_color=error_text_color)
            self.link_entry.configure(border_color=(colors['danger_600'], colors['danger_400']))
            self.video_radiobutton.configure(state='disabled')
            self.audio_radiobutton.configure(state='disabled')
            self.download_button.configure(state='disabled')
            return False

    def video_audio_filter(self):
        link_is_valid = self.youtube_link_is_valid()
        self.download_error_label.configure(text='')
        if link_is_valid:
            try:
                video_radio_values = video_filter(self.youtube_link.youtube_link)
                audio_radio_values = audio_filter(self.youtube_link.youtube_link)

                if self.radio_var.get() == 1:
                    self.option_menu_var.set(value='Video Resolution')
                    self.option_menu.configure(values=video_radio_values)
                elif self.radio_var.get() == 2:
                    self.option_menu_var.set(value='Audio Bitrate')
                    self.option_menu.configure(values=audio_radio_values)
            except pytube.exceptions.PytubeError as e:
                self.download_error_label.configure(text=e,
                                                    text_color=error_text_color)

    def radio_button_callback(self):
        thread = threading.Thread(target=self.video_audio_filter)
        thread.start()

    def get_optionmenu_value(self):
        value = self.option_menu_var.get()
        if self.radio_var.get() == 1:
            if value == 'Video Resolution':
                self.download_error_label.configure(text='Warning: Select Video Resolution.',
                                                    text_color=warning_text_color)
            else:
                self.download_error_label.configure(text='')
                return value.split('|')[0].strip()
        elif self.radio_var.get() == 2:
            if value == 'Audio Bitrate':
                self.download_error_label.configure(text='Warning: Select Audio Bitrate.',
                                                    text_color=warning_text_color)
            else:
                self.download_error_label.configure(text='')
                return value.split('|')[0].strip()
        else:
            self.download_error_label.configure(text='Warning: Specify Download Type.',
                                                text_color=warning_text_color)

    def download(self):
        self.progress_frame.winfo_children()[0].configure(text='')
        self.progress_frame.winfo_children()[1].configure(text='0%')
        self.progress_frame.winfo_children()[2].set(0)
        self.progress_frame.winfo_children()[3].configure(text='')
        if self.youtube_link_is_valid():
            try:
                yt_link = self.youtube_link.youtube_link
                yt_obj = YouTube(yt_link, on_progress_callback=self.on_progress)
                download_type = self.get_optionmenu_value()
                if download_type is not None and download_type.endswith('p'):
                    download_location = filedialog.askdirectory()
                    if download_location:
                        # Create a Video folder inside the parent download location
                        video_folder = os.path.join(download_location, 'Video')
                        os.makedirs(video_folder, exist_ok=True)

                        video = yt_obj.streams.get_by_resolution(download_type)
                        self.progress_frame.winfo_children()[0].configure(text='Downloading...',)
                        self.progress_frame.winfo_children()[3].configure(text=yt_obj.title)
                        video.download(output_path=video_folder)
                        self.progress_frame.winfo_children()[0].configure(text='Download Done.',)
                elif download_type is not None and download_type.endswith('kbps'):
                    download_location = filedialog.askdirectory()
                    if download_location:
                        # Create an Audio folder inside the parent download location
                        audio_folder = os.path.join(download_location, 'Audio')
                        os.makedirs(audio_folder, exist_ok=True)

                        audio_stream = get_audio_stream(yt_obj, download_type)
                        self.progress_frame.winfo_children()[0].configure(text='Downloading...', )
                        self.progress_frame.winfo_children()[3].configure(text=yt_obj.title)
                        audio_stream.download(output_path=audio_folder)
                        self.progress_frame.winfo_children()[0].configure(text='Download Done.', )

            except pytube.exceptions.PytubeError:
                self.download_error_label.configure(text='Error: Unable to download video.',
                                                    text_color=error_text_color)

    def on_download(self):
        thread = threading.Thread(target=self.download)
        thread.start()

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100
        percent = str(int(percentage_of_completion))
        self.progress_frame.winfo_children()[1].configure(text=f'{percent}%')
        self.progress_frame.winfo_children()[1].update()

        # Update Progress Bar
        self.progress_frame.winfo_children()[2].set(float(percentage_of_completion / 100))

    def paste_button_event(self):
        try:
            # Get the text from the clipboard
            pasted_text = self.clipboard_get()

            # Insert the text into the Entry Widget
            self.link_entry.winfo_children()[0].delete(0, 'end')
            self.link_entry.winfo_children()[0].insert(0, pasted_text)
            self.youtube_link_is_valid()
            self.video_audio_filter()
        except TclError:
            pass

    def on_paste(self):
        thread = threading.Thread(target=self.paste_button_event)
        thread.start()


if __name__ == '__main__':
    app = App()
    app.mainloop()
