from pytube import YouTube


def video_filter(link: str) -> list:
    yt = YouTube(link)

    video_streams = yt.streams.filter(file_extension="mp4", progressive=True)
    resolutions_and_sizes = [(video_stream.resolution, video_stream.filesize_mb) for video_stream in video_streams]
    formated_list = ["{} | {:.2f} mb".format(resolution, size) for resolution, size in resolutions_and_sizes]
    return formated_list


def audio_filter(link: str) -> list:
    yt = YouTube(link)

    audio_streams = yt.streams.filter(file_extension="mp4", only_audio=True)
    audio_bitrates_and_sizes = [(audio_stream.abr, audio_stream.filesize_mb) for audio_stream in audio_streams]
    formated_list = ["{} | {:.2f} mb".format(bitrate, size) for bitrate, size in audio_bitrates_and_sizes]
    return formated_list



def get_audio_stream(yt_obj, desired_abr: str):
    selected_audio_stream = None
    audio_streams = yt_obj.streams.filter(file_extension="mp4", only_audio=True)
    for stream in audio_streams:
        if stream.abr == desired_abr:
            selected_audio_stream = stream
            break

    return selected_audio_stream
