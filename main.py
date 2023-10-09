import customtkinter as ctk
from tkinter import filedialog
from tkinter import *
from PIL import Image
from pytube import YouTube
import pytube.exceptions
import os
import threading

# Set Application Appearance and Color Theme
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

# Set Application Width and Height
appWidth, appheight = 600, 300

# Set Icons path
current_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Assets')


class App(ctk.CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Place App in Center of Screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - appWidth) // 2
        y = (screen_height - appheight) // 2

        # Create Window
        self.geometry(f'{appWidth}x{appheight}+{x}+{y}')
        self.resizable(False, False)
        self.title('YouTube Downloader')
        self.iconbitmap('Assets/Icon.ico')

        # Configure App Column
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Configure App Row
        self.rowconfigure(1, weight=1)

        # Add App Label
        self.app_label = ctk.CTkLabel(self, text='YOUTUBE DOWNLOADER\n VIDEO | AUDIO',
                                      font=('sans serif', 20, 'bold'))
        self.app_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky='ew')

        # Create Frame
        self.downloadframe = DownloadFrame(self)
        self.downloadframe.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 0), sticky='nsew')

        # Author
        self.author = ctk.CTkLabel(self, text='C.Sarmiento 2023 Version 1.1', font=('helvetica', 10))
        self.author.grid(row=2, column=0, padx=10, sticky='w')

        # Run Application
        self.mainloop()


class DownloadFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Define StringVar
        self.url = StringVar()
        self.radio_var = IntVar(value=0)

        # Frame Columns
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Load Icons
        self.paste_icon = ctk.CTkImage(Image.open(os.path.join(current_path, 'paste-light.png')),
                                       size=(20, 20))
        self.download_icon = ctk.CTkImage(Image.open(os.path.join(current_path, 'download.png')),
                                          size=(20, 20))

        # Labels
        self.download_label = ctk.CTkLabel(self, text='Insert Video Link:', font=('roboto', 15))
        self.download_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.download_status = ctk.CTkLabel(self, text='Waiting for input...', font=('roboto', 12))
        self.download_status.grid(row=1, column=1, padx=10, sticky='e')

        self.download_progress = ctk.CTkLabel(self, text='0%', font=('lucida sans unicode', 12))
        self.download_progress.grid(row=3, column=1, padx=10, pady=10, sticky='e')

        self.download_video_title = ctk.CTkLabel(self, text='')
        self.download_video_title.grid(row=4, column=0, columnspan=2, padx=10, sticky='ew')

        # Entry
        self.download_entry = ctk.CTkEntry(self, border_color='#40F8FF', textvariable=self.url,
                                           validatecommand=self.is_valid)
        self.download_entry.grid(row=0, column=0, columnspan=2, padx=(140, 50), pady=10, sticky='ew')
        self.download_entry.bind('<KeyRelease>', self.is_valid)

        # Button
        self.download_button = ctk.CTkButton(self, text='Download', image=self.download_icon, compound='left',
                                             command=self.on_download_button_click)
        self.download_button.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

        self.paste_button = ctk.CTkButton(self, text='', image=self.paste_icon, width=0,
                                          fg_color='transparent', hover_color=('gray70', 'gray30'),
                                          command=self.paste_button_event)
        self.paste_button.grid(row=0, column=1, padx=10, pady=10, sticky='e')

        # Radio Buttons
        self.download_video = ctk.CTkRadioButton(self, text='Video', variable=self.radio_var, value=1)
        self.download_video.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.download_audio = ctk.CTkRadioButton(self, text='Audio', variable=self.radio_var, value=2)
        self.download_audio.grid(row=2, column=0, padx=10, pady=10, sticky='e')

        # Progress Bar
        self.download_progressbar = ctk.CTkProgressBar(self, orientation='horizontal')
        self.download_progressbar.set(0)
        self.download_progressbar.grid(row=3, column=0, columnspan=2, padx=(10, 50), sticky='ew')

    def is_valid(self, event):
        yt_link = self.url.get()
        try:
            if len(yt_link) != 0:
                YouTube(yt_link)
                self.download_entry.configure(border_color='#16FF00')
                self.download_status.configure(text='Ready', text_color='#16FF00')
                return True
            else:
                self.download_entry.configure(border_color='#FE0000')
                self.download_status.configure(text='Waiting for input...', text_color='#F0F0F0')
                return False
        except pytube.exceptions.ExtractError:
            self.download_entry.configure(border_color='#FE0000')
            self.download_status.configure(text='Invalid Youtube Link', text_color='#FE0000')
            return False

    def download(self):
        self.download_video_title.configure(text='')
        self.download_progress.configure(text='0%')
        self.download_progressbar.set(0)
        if self.is_valid(None):
            try:
                yt_link = self.url.get()
                yt_obj = YouTube(yt_link, on_progress_callback=self.on_progress)
                download_location = filedialog.askdirectory()
                if download_location:
                    # Download Video
                    if self.radio_var.get() == 1:
                        # Create a Video folder inside the parent download location
                        video_folder = os.path.join(download_location, 'Video')
                        os.makedirs(video_folder, exist_ok=True)

                        video = yt_obj.streams.get_highest_resolution()
                        self.download_status.configure(text='Downloading...')
                        self.download_video_title.configure(text=yt_obj.title)
                        video.download(output_path=video_folder)
                        self.download_status.configure(text='Download Done', text_color='#16FF00')

                    # Download Audio
                    elif self.radio_var.get() == 2:
                        # Create an Audio folder inside the parent download location
                        audio_folder = os.path.join(download_location, 'Audio')
                        os.makedirs(audio_folder, exist_ok=True)

                        audio = yt_obj.streams.get_audio_only('mp4')
                        self.download_status.configure(text='Downloading...')
                        self.download_video_title.configure(text=yt_obj.title)
                        audio.download(output_path=audio_folder)
                        self.download_status.configure(text='Download Done', text_color='#16FF00')
                    else:
                        self.download_status.configure(text='Specify download type', text_color='#FE0000')
            except pytube.exceptions.PytubeError:
                self.download_status.configure(text='Unable to download video', text_color='#FE0000')
        else:
            self.download_status.configure(text='No Link Entered', text_color='#FE0000')

    # Download Button Event Function
    def on_download_button_click(self):
        thread = threading.Thread(target=self.download)
        thread.start()

    # Progressbar Function
    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100
        percent = str(int(percentage_of_completion))
        self.download_progress.configure(text=f'{percent}%')
        self.download_progress.update()

        # Update Progress Bar
        self.download_progressbar.set(float(percentage_of_completion / 100))

    # Create a Paste Button Function
    def paste_button_event(self):
        # Get the text from the clipboard
        pasted_text = self.clipboard_get()

        # Insert the text into the link entry widget
        self.download_entry.delete(0, 'end')
        self.download_entry.insert(0, pasted_text)


if __name__ == '__main__':
    App()
