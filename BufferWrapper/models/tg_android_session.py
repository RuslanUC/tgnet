from BufferWrapper.models.headers import Headers


class TGAndroidSession:
    headers: Headers
    datacenters = []

    def __str__(self):
        """
        :return: `DC: 4 | en-US`
        """
        res = ''
        if hasattr(self.headers, 'currentDatacenterId'):
            res += f'DC: {self.headers.currentDatacenterId}'

        if hasattr(self.headers, 'lastInitSystemLangcode'):
            res += f' | {self.headers.lastInitSystemLangcode}'

        return res
