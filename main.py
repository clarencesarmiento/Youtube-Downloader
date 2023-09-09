import customtkinter as ctk
from tkinter import filedialog
from tkinter import *
from pytube import YouTube
import pytube.exceptions

ctk.set_appearance_mode('system')
ctk.set_default_color_theme('blue')


appWidth, appheight = 600, 320


class MyTabview(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Define StringVar
        self.url = StringVar()

        # Create Tabs
        download_tab = self.add('Download')
        convert_tab = self.add('Convert')

        # ----------------------------------------------- Download Tab ----------------------------------------------- #
        # Configure Tab
        self.tab('Download').columnconfigure(0, weight=1)
        self.tab('Download').columnconfigure(1, weight=1)

        # Labels
        self.download_label = ctk.CTkLabel(download_tab, text='Insert Video Link:', font=('century gothic', 15))
        self.download_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.download_status = ctk.CTkLabel(download_tab, text='Waiting for input...', font=('lucida sans unicode', 12))
        self.download_status.grid(row=1, column=0, padx=10, pady=10, sticky='e')

        self.download_progress = ctk.CTkLabel(download_tab, text='0%', font=('lucida sans unicode', 12))
        self.download_progress.grid(row=2, column=1, padx=10, pady=10, sticky='e')

        # Entry
        self.download_entry = ctk.CTkEntry(download_tab, border_color='#40F8FF', textvariable=self.url,
                                           validatecommand=self.is_valid)
        self.download_entry.grid(row=0, column=0, columnspan=2, padx=(140, 10), pady=10, sticky='ew')
        self.download_entry.bind('<KeyRelease>', self.is_valid)

        # Button
        self.download_button = ctk.CTkButton(download_tab, text='Download', command=self.download)
        self.download_button.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        self.download_button.configure(state='disabled')

        # Progress Bar
        self.download_progressbar = ctk.CTkProgressBar(download_tab, orientation='horizontal')
        self.download_progressbar.set(0)
        self.download_progressbar.grid(row=2, column=0, columnspan=2, padx=(10, 50), pady=10, sticky='ew')

    def is_valid(self, event):
        yt_link = self.url.get()
        try:
            if len(yt_link) != 0:
                YouTube(yt_link)
                self.download_entry.configure(border_color='#16FF00')
                self.download_button.configure(state='normal')
                self.download_status.configure(text='Ready', text_color='#16FF00')
                return True
            else:
                self.download_entry.configure(border_color='#FE0000')
                self.download_button.configure(state='disabled')
                self.download_status.configure(text='Waiting for input...', text_color='#F0F0F0')
                self.download_progress.configure(text='0%')
                self.download_progressbar.set(0)
                return False
        except pytube.exceptions.ExtractError:
            self.download_entry.configure(border_color='#FE0000')
            self.download_button.configure(state='disabled')
            self.download_status.configure(text='Invalid Youtube Link', text_color='#FE0000')
            self.download_progress.configure(text='0%')
            self.download_progressbar.set(0)
            return False

    def download(self):
        if self.is_valid:
            try:
                yt_link = self.url.get()
                yt_obj = YouTube(yt_link, on_progress_callback=self.on_progress)
                video = yt_obj.streams.get_highest_resolution()
                download_location = filedialog.askdirectory()
                if download_location:
                    video.download(output_path=download_location)
                    self.download_status.configure(text='Download Done', text_color='#16FF00')
            except pytube.exceptions.PytubeError:
                self.download_status.configure(text='Download Failed', text_color='#FE0000')

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100
        percent = str(int(percentage_of_completion))
        self.download_progress.configure(text=f'{percent}%')
        self.download_progress.update()

        # Update Progress Bar
        self.download_progressbar.set(float(percentage_of_completion / 100))

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
        self.title('YouTube Downloader/Converter')

        # Configure App Column
        self.columnconfigure(0, weight=1)

        # Configure App Row
        self.rowconfigure(1, weight=1)

        # Add App Label
        self.app_label = ctk.CTkLabel(self, text='YOUTUBE VIDEO \n DOWNLOADER / CONVERTER',
                                      font=('sans serif', 20, 'bold'))
        self.app_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky='ew')

        # Create Tabview
        self.tab_view = MyTabview(self)
        self.tab_view.grid(row=1, column=0, columnspan=2, rowspan=2, padx=10, pady=10, sticky='nsew')

        self.mainloop()


if __name__ == '__main__':
    App()
