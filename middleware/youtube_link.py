class YouTubeLink:
    def __init__(self):
        self._link = None

    @property
    def youtube_link(self) -> str:
        return self._link

    @youtube_link.setter
    def youtube_link(self, link: str):
        if link is None or link == '':
            raise ValueError('Warning: Link cannot be empty.')

        self._link = link
