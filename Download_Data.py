# -*- coding: utf-8 -*-
import scrapetube
import codecs
from pytube import (YouTube,request)
class getLinks():
    def __init__(self):
        self.Links : list = []
        self.Fehler: list = []
        self.data : dict = {}

    def search_Pytube(self,link:str)->(list,list,dict):
        self.Links.append(link)
        for i in range(3):
            try:
                self.youtubeObject = YouTube(link)
                title = self.youtubeObject.title
                self.data[link]= ["Wartet",title,True]
                break
            except:
                continue
        else:
            self.Fehler.append(link)
            self.data[link] = ["Fehler", "Video nicht verfügbar/ nicht öffentlich",False]
        return self.Links, self.Fehler, self.data

    def playlist(self,link:str)->(list,list,dict):  # Prüft ob Link der Playlist gültig ist
        url = "https://www.youtube.com/watch?v="
        playlist_link = link.split("list=")[1].strip()
        num = 0
        try:
            videos = scrapetube.get_playlist(playlist_link)
            for video in videos:
                video_link = url + video['videoId']
                title = video["title"]["runs"][0]["text"]
                self.Links.append(video_link)
                self.data[video_link] = ["Wartet",title,True]
            if self.data == {}:
                self.Links.append(link)
                self.Fehler.append(link)
                self.data[link] = ["Playlist nicht verfügbar/ nicht öffentlich","Fehler",False]
        except:
            self.Links.append(link)
            self.Fehler.append(link)
            self.data[link] = ["Keine Internetverbindung","Fehler",False]
        return self.Links,self.Fehler,self.data

    def new_vid(self,link:str,max_results:int = 3)->(list,list,dict):
        url = "https://www.youtube.com/watch?v="
        error_count: int = 0
        ch_names = []
        if link[-4:] == ".txt":
            with codecs.open(link, "r+", "utf-8") as f:
                for i, line in enumerate(f):
                    sv = line.strip().replace("\n", "").split(" ")
                    for elem in sv:
                        if elem in [""," "]:
                            continue
                        ch_names.append(elem.lower())
        else:
            links = link.split(" ")
            for elem in links:
                if elem in ["", " "]:
                    continue
                ch_names.append(elem.lower())
        for j,ch_name in enumerate(ch_names):
            index = j+j*max_results-max_results*error_count
            try:
                videos = scrapetube.get_channel(channel_url=f"https://youtube.com/@{ch_name}/videos",
                                                sort_by="newest", limit=int(max_results))
                for video in videos:
                    video_link = url + video['videoId']
                    title = video["title"]["runs"][0]["text"]
                    self.Links.append(video_link)
                    self.data[video_link] = ["Wartet",title,True]

                self.data[f"##{j}##"] = ["#####",ch_name,False]
                self.Links.insert(index, f"##{j}##")
            except Exception as e:
                error_count+=1
                if "[Errno 11001]" in str(e):
                    self.data[ch_name] = ["Keine Internetverbindung","Fehler",False]
                else:
                    self.data[ch_name] = ["Unbekannter Kanalname","Fehler",False]
                self.Fehler.append(ch_name)
                self.Links.append(ch_name)
        return self.Links, self.Fehler, self.data

    def openfile(self,link:str)->(list,list,dict): # öffnet Dokument mit Links
        links = []
        with codecs.open(link, "r+", "utf-8") as f:
            for i, line in enumerate(f):
                sv = line.split(" ")
                for elem in sv:
                    if elem[:8] == "https://":
                        elem = elem.replace("youtu.be", "youtube.com").strip()
                        links.append(elem.replace("\n", "").strip())
        for elem in links:
            self.search_Pytube(elem)
        return self.Links, self.Fehler, self.data
