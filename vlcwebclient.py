# -*- coding: UTF-8 -*-
# Information taken from
# http://git.videolan.org/?p=vlc.git;a=blob_plain;f=share/lua/http/requests/+
# +README.txt;hb=HEAD
#
# This module tries to mostly provide a similar interface to
# https://github.com/DerMitch/py-vlcclient
#
__author__ = 'Florian Jung <jungflor@gmail.com>'
__version__ = "0.1.0"
__license__ = "MIT License"

import requests
import urlparse


class WrongPasswordError(Exception):
    """
    Invalid password sent to the server
    """
    pass


class VLCWebClient(object):
    def __init__(self, settings):
        self.address = settings.get("address", "127.0.0.1")
        self.port = settings.get("port", 8080)
        self.username = settings.get("username", "")
        self.password = settings.get("password", "")
        self.timeout = settings.get("timeout", 5)

        self._session = requests.Session()
        if self.username or self.password:
            self._session.auth = (self.username, self.password)


    def _send(self, apiUri, format='json', **kwargs):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(
            self.address)
        if not netloc:
            netloc = self.address
        if scheme == "":
            scheme = "http"
        if self.port != 80:
            netloc += ":{}".format(self.port)
        path = apiUri
        url = urlparse.urlunparse(
            (scheme, netloc, path, params, query, fragment))
        res = self._session.get(url, params=kwargs, timeout=self.timeout)

        if res.status_code == 401:
            raise WrongPasswordError('Incorrect username/password')
        res.raise_for_status()
        if format == 'json':
            try:
                return res.json()
            except:
                if res.text.startswith("<html"):
                    # got error
                    raise ValueError("Error sending")
                raise
        else:
            return res.text


    def _send_command(self, **kwargs):
        return self._send("/requests/status.json", **kwargs)


    def status(self):
        return self._send_command()


    def info(self):
        """
        information about current stream
        """
        status = self.status()
        return status['information']


    def play(self, item=None, option=None):
        """
        if item is a uri:
            add <uri> to playlist and start playback:
              ?command=in_play&input=<uri>&option=<option>
        if item is int or None:
            play playlist item <id>. If <id> is omitted, play last active item:
                ?command=pl_play&id=<id>
        :param item: item to play (playlist id or uri)
        :param option: the option field is optional, and can have the values:
            noaudio
            novideo
            (only if item is uri)
        :return:
        """
        id = None
        try:
            if item is not None:
                id = int(item)
        except:
            if option:
                return self._send_command(command="in_play", input=item,
                                          option=option)
            else:
                return self._send_command(command="in_play", input=item)

        if id is not None:
            return self._send_command(command="pl_play", id=id)
        else:
            return self._send_command(command="pl_play")


    def enqueue(self, uri):
        """
        add <uri> to playlist:
            ?command=in_enqueue&input=<uri>

        :param uri:
        :return:
        """
        return self._send_command(command="in_enqueue", input=uri)


    def togglePlay(self, id=None):
        """
        toggle pause.
        If current state was 'stop', play item <id>, if no <id> specified,
        play current item.
        If no current item, play 1st item in the playlist:
            ?command=pl_pause&id=<id>

        :param id: item id to play
        :return:
        """
        if id is not None:
            return self._send_command(command="pl_pause", id=id)
        else:
            return self._send_command(command="pl_pause")


    def pause(self):
        """
        pause playback, do nothing if already paused
            ?command=pl_forcepause

        :return:
        """
        return self._send_command(command="pl_forcepause")


    def resume(self):
        """
        resume playback if paused, else do nothing
            ?command=pl_forceresume

        :return:
        """
        return self._send_command(command="pl_forceresume")


    def stop(self):
        """
        stop playback:
            ?command=pl_stop

        :return:
        """
        return self._send_command(command="pl_stop")


    def rewind(self):
        """
        Rewind stream

        :return:
        """
        return self.seek("0%")


    def next(self):
        """
        jump to next item:
            ?command=pl_next

        :return:
        """
        return self._send_command(command="pl_next")


    def previous(self):
        """
        jump to previous item:
            ?command=pl_previous

        :return:
        """
        return self._send_command(command="pl_previous")


    def prev(self):
        """
        jump to previous item:
            ?command=pl_previous

        :return:
        """
        return self.previous()


    def delete(self, id):
        """
        delete item <id> from playlist:
            ?command=pl_delete&id=<id>
            NOTA BENE: pl_delete is completly UNSUPPORTED

        :param id: item
        :return:
        """
        return self._send_command(command="pl_delete", id=id)


    def empty(self):
        """
        empty playlist:
            ?command=pl_empty

        :return:
        """
        return self._send_command(command="pl_empty")


    def clear(self):
        """
        Clear all items in playlist

        :return:
        """
        return self.empty()


    def sort(self, sortMode, reversed=False):
        """
        sort playlist using sort mode <val> and order <id>:
          ?command=pl_sort&id=<id>&val=<val>
          If id=0 then items will be sorted in normal order, if id=1
          they will be sorted in reverse order

        :param sortMode: A non exhaustive list of sort modes:
            0 Id
            1 Name
            3 Author
            5 Random
            7 Track number
        :param reversed: sort in reverse order
        :return:
        """
        val = sortMode
        id = 1 if reversed else 0
        return self._send_command(command="pl_sort", id=id, val=val)


    def random(self):
        """
        toggle random playback:
            ?command=pl_random

        :return:
        """
        return self._send_command(command="pl_random")


    def loop(self):
        """
        toggle loop:
            ?command=pl_loop

        :return:
        """
        return self._send_command(command="pl_loop")


    def repeat(self):
        """
        toggle repeat:
            ?command=pl_repeat

        :return:
        """
        return self._send_command(command="pl_repeat")


    def fullscreen(self):
        """
        toggle fullscreen:
            ?command=fullscreen

        :return:
        """
        return self._send_command(command="fullscreen")


    def volume(self, val=None):
        """
        if val:
            set volume level to <val> (can be absolute integer,
            percent or +/- relative value):
              ?command=volume&val=<val>
              Allowed values are of the form:
                +<int>, -<int>, <int> or <int>%
        else:
            return volume

        :param uri:
        :return:
        """
        if val is None:
            res = self.status()
            return res['volume']
        return self._send_command(command="volume", val=val)


    def volup(self, steps=1):
        """
        increase colume by steps

        :param steps: number of values to increase by (default: 1)
        :return:
        """
        self.volume("+{}".format(steps))


    def voldown(self, steps=1):
        """
        decrease colume by steps

        :param steps: number of values to decrease by (default: 1)
        :return:
        """
        self.volume("-{}".format(steps))


    def mute(self):
        return self.volume(0)


    def seek(self, val):
        """
        seek to <val>:
          ?command=seek&val=<val>
          Allowed values are of the form:
            [+ or -][<int><H or h>:][<int><M or m or '>:]
            [<int><nothing or S or s or ">]
            or [+ or -]<int>%
            (value between [ ] are optional, value between < > are mandatory)
          examples:
            1000 -> seek to the 1000th second
            +1H:2M -> seek 1 hour and 2 minutes forward
            -10% -> seek 10% back

        :param val:
        :return:
        """
        return self._send_command(command="seek", val=val)


    def playlist(self):
        """
        get the full playlist tree

        NB: playlist_jstree.xml is used for the internal web client.
            It should not be relied upon by external remotes.
            It may be removed without notice.

        :return:
        """
        return self._send("/requests/playlist.json")


    def browse(self, uri):
        """
        get file list from uri. At the moment, only local file uris are
        supported
            ?dir=<uri>

            NB: uri is the preferred parameter. Dir is deprecated and may be
                removed in a future release.

        :param uri:
        :return:
        """
        return self._send("/requests/browse.json", dir=uri)


    def vlm(self, command=None):
        """
        if command:
            execute VLM command <cmd>
                ?command=<cmd>

            get the error message from <cmd>
        else:
            get the full list of VLM elements

        :param command:
        :return:
        """
        if command is None:
            return self._send("/requests/vlm.xml", format="xml")
        else:
            return self._send("/requests/vlm_cmd.xml", format="xml",
                              command=command)


if __name__ == "__main__":
    vlc = VLCWebClient({"password": ""})
    import pprint

    pprint.pprint(vlc.status())
