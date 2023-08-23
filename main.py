# -*- coding: utf-8 -*-
import kivy
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window
Window.softinput_mode = "below_target"
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context #https überprüfung umgehen
import webbrowser
import Download_Data
import time
import threading
import codecs
from pytube import (YouTube,request)
#from android.permissions import request_permissions, Permission
#request_permissions([Permission.INTERNET,Permission.WRITE_EXTERNAL_STORAGE,Permission.READ_EXTERNAL_STORAGE])

class WindowManager(ScreenManager):
    pass

class Seite_1(Screen):
    def __init__(self, **kwargs):
        super(Seite_1, self).__init__(**kwargs)
        self.btn = ObjectProperty(None)
        self.btn2 = ObjectProperty(None)
        self.btn3 = ObjectProperty(None)
        self.btn4 = ObjectProperty(None)
        self.label = ObjectProperty(None)
        self.label2 = ObjectProperty(None)
        self.label3 = ObjectProperty(None)
        self.slider = ObjectProperty(None)
        self.textinput = ObjectProperty(None)
        self.textinput2 = ObjectProperty(None)
        self.checked = False            # wenn check-entry erfolgreich

    def add_Dropdown(self,val:int):
        if val == 0:
            data = ["Video(mp4)","Audio(mp3)"]
            caller = self.btn
        elif val == 1:
            data = ["bestmögliche Auflösung", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p",
                    "niedrigste Auflösung"]
            caller = self.btn2
        else:
            data = ["einzelnes Video herunterladen","Playlist herunterladen",
                    "Videolinks aus Dokument importieren","Neueste Videos"]
            caller = self.btn3
        menu_items = [
            {
                "text": f"{elem}",
                "viewclass": "OneLineListItem",
                "height": dp(54),
                "on_release": lambda x=f"Item {elem}": self.menu_callback(x,caller,val),
            } for elem in data
        ]
        self.menu = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            position = "center",
            width_mult=3,
            border_margin=dp(24)
        )
        self.menu.open()

    def menu_callback(self, text_item:str,caller,val:int):
        text = text_item.replace("Item","").strip()
        caller.text = text
        if val == 0:
            self.enable_res()
        elif val == 2:
            self.enable_slider()
        self.menu.dismiss()

    def open_url(self):                 #öffnet ausgewählten Link
        webbrowser.open_new_tab("https://www.youtube.com/")

    def enable_res(self):
        if self.btn.text == "Audio(mp3)":
            self.btn2.disabled = True
        else:
            self.btn2.disabled = False

    def enable_slider(self):
        auswahl = self.btn3.text
        if auswahl == "Neueste Videos":
            self.label2.text = "Bitte Kanalname oder Dateipfad eingeben:"
            self.slider.disabled = False
            self.label3.disabled = False
            self.btn4.disabled = False
            return
        elif auswahl == "Videolinks aus Dokument importieren":
            self.label2.text = "Bitte Dateipfad eingeben:"
            self.btn4.disabled = False
        else:
            self.label2.text = "Bitte Link eingeben:"
            self.btn4.disabled = True
        self.slider.disabled = True
        self.label3.disabled = True
        self.slider.value = 1

    def setVal(self,val:int):
        OpenFile(val)

    def check_entry(self):
        destination,mode,input = self.textinput.text,self.btn3.text,self.textinput2.text
        if not os.path.exists(destination) or destination == "":
            self.error_popup(f"{self.label.text}\nDateipfad ist ungültig")
            return
        try:
            with open(f"{destination}/check.txt", "w") as f:
                f.write("123Test")
            os.remove(f"{destination}/check.txt")
        except:
            self.error_popup(f"{self.label.text}\nKein Zugriff auf gewählten Ordner möglich")
            return
        if input == "":
            self.error_popup(f"{self.label2.text}\nUngültige Eingabe")
            return
        if input[-4:] in [".txt",".odt",".docx"] and mode in["einzelnes Video herunterladen","Playlist herunterladen"]:
            self.error_popup(f"{self.label2.text}\nUngültige Eingabe")
            return
        elif mode == "Videolinks aus Dokument importieren":
            if input[-4:] != ".txt":
                self.error_popup(f"{self.label2.text}\nDateiformat wird nicht unterstützt!(->.txt,.odt.docx)")
                return
            elif not os.path.exists(input):
                self.error_popup(f"{self.label2.text}\nDateipfad ist ungültig")
                return
        elif mode == "Neueste Videos":
            if os.path.exists(input) and input[-4:] not in [".txt",".odt",".docx"]:
                self.error_popup(f"{self.label2.text}\nDateiformat wird nicht unterstützt!(->.txt,.odt.docx)")
                return
            elif not os.path.exists(input) and input[-4:] in [".txt",".odt",".docx"]:
                self.error_popup(f"{self.label2.text}\nDateipfad ist ungültig")
                return
        self.manager.current = "Übersicht"
        self.checked = True

    def getData(self):
        mode,input,hits = self.btn3.text,self.textinput2.text,self.slider.value
        functions = {"Videolinks aus Dokument importieren": Download_Data.getLinks().openfile,
                     "Neueste Videos": Download_Data.getLinks().new_vid,
                     "einzelnes Video herunterladen": Download_Data.getLinks().search_Pytube,
                     "Playlist herunterladen": Download_Data.getLinks().playlist}
        func = functions.get(mode)
        if mode == "Neueste Videos":
            links, fehler, data = func(input, int(hits))
        else:
            links, fehler, data = func(input)
        return links, fehler, data

    def error_popup(self, text: str):
        pop = Popup(title='Fehler',
                    content=Label(text=text, text_size=(self.width * 0.6, None),
                                  size=self.size, halign='left', valign='center'),
                    size_hint=(0.7, 0.2))
        pop.open()

class OpenFile(Screen):
    def __init__(self,val:int=None,**kwargs):
        super(OpenFile, self).__init__(**kwargs)
        global Val;Val = val

    def openFile(self,filepath:str, filepathname: str):
            if Val == 0:
                self.manager.ids.main.ids.textinput.text = filepath
            elif Val == 1 and filepathname != [] :
                self.manager.ids.main.ids.textinput2.text = filepathname[0]

    def createPopup(self):
        box = FloatLayout()
        self.input = TextInput(text='Neuer Ordner', multiline=False,pos_hint= {"x":0.01, "top":0.85},size_hint =(0.98, 0.3))
        box.add_widget(self.input)
        btn1 = Button(text="Abbrechen", pos_hint= {"x":0.08, "top":0.45},size_hint=(0.4, 0.3))
        btn2 = Button(text="Erstellen", pos_hint= {"x":0.53, "top":0.45},size_hint=(0.4, 0.3))
        box.add_widget(btn1)
        box.add_widget(btn2)
        popup = Popup(title="Ordner erstellen",
                      title_align='center', content=box,
                      size_hint=(0.7,0.2),
                      auto_dismiss=True)
        btn1.bind(on_press=popup.dismiss)
        btn2.bind(on_press=lambda x: [self.create_new_folder(self.input.text),popup.dismiss()])
        popup.open()

    def create_new_folder(self,filename:str):
        for i in ["/", ":", "*", "<", ">", "|", "?", '"', "\\"]:
            filename = filename.replace(i, "")
        filename = filename.strip()
        try:
            os.makedirs(f"{self.manager.ids.openfile.ids.filechooser.path}/{filename}", exist_ok=True)
            self.manager.ids.openfile.ids.filechooser._update_files()
        except:
            pop = Popup(title='Fehler',
                        content=Label(text="Zugriff verweigert"),
                        size_hint=(0.7, 0.2))
            pop.open()

class Seite_2(Screen):
    def __init__(self, **kwargs):
        super(Seite_2, self).__init__(**kwargs)
        self.label = ObjectProperty(None)
        self.percent = ObjectProperty(None)
        self.pb_1 = ObjectProperty(None)
        self.percent2 = ObjectProperty(None)
        self.pb_2 = ObjectProperty(None)
        self.btn = ObjectProperty(None)
        self.btn2 = ObjectProperty(None)
        self.btn3 = ObjectProperty(None)

    def resetBtn(self):
        self.btn.text = "Start"
        self.btn.disabled = False
        self.percent.text = "0 %"
        self.pb_1.value = 0
        self.percent2.text = "0 %"
        self.pb_2.value = 0
        self.btn3.pos_hint = {"x":1.5, "top":0.1}
        self.btn.pos_hint = {"x":0.25, "top":0.1}; self.btn2.pos_hint = {"x":0.51, "top":0.1}
        Youtube_App.pause = True
        
class Youtube_App(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.only_audio = False
        self.changed = False

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        Builder.load_file("main.kv")
        return WindowManager()

    def change_screen(self, screen: str):
        self.root.current = screen

    def add_datatable(self,data):
        self.Links,self.Fehler,self.Data = data
        self.data_tables = MDDataTable(
            pos_hint={'x': 0.01, 'top': 0.88},
            size_hint=(0.98, 0.64),
            check=True,
            use_pagination = True,
            rows_num = 5,
            pagination_menu_height="240dp",
            pagination_menu_pos="center",
            elevation=2,
            background_color_header="#65275d",
            column_data=[
                ("Nr.", dp(20)),
                ("Status", dp(40)),
                ("Titel", dp(100)),
            ],
            row_data = [])
        self.data_tables.bind(on_check_press=self.on_check_press)
        self.addRow()
        self.initCheckboxes()
        self.data_tables.header.disabled = True
        self.root.ids.data_tab.ids.data_layout.add_widget(self.data_tables)
        self.event = Clock.schedule_interval(lambda dt : self.initCheckboxes(),0.5)

    def addRow(self):
        for i,link in enumerate(self.Links):
            status,titel,check = self.Data[link]
            if status == "#####":
                icon = link
            elif check == True:
                icon = ("alert", [255 / 256, 165 / 256, 0, 1], f"{status}")
            else:
                icon = ("alert-circle", [1, 0, 0, 1], f"{status}")
            self.data_tables.add_row((f"{i + 1}",icon,titel))

    def initCheckboxes(self):
        list_len = len(self.Links)
        list_indexes = [i for i in range(list_len)]
        rows_num = self.data_tables.table_data.rows_num
        dict = {}
        pages = list_len // rows_num
        for page in range(pages):
            subset = list_indexes[(rows_num*page):(rows_num*(page+1))]
            final_list = []
            for i,index in zip(range(rows_num),subset):
                check = self.Data[self.Links[index]][2]
                if check:
                    final_list.append(i*3)
            dict[page] = final_list
        if rows_num * pages != len(list_indexes):
            subset = list_indexes[rows_num * pages:]
            final_list = []
            for i,index in zip(range(rows_num),subset):
                check = self.Data[self.Links[index]][2]
                if check:
                    final_list.append(i * 3)
            dict[pages] = final_list
        self.data_tables.table_data.current_selection_check = dict

    def stop_update(self):
        Clock.unschedule(self.event)

    def on_check_press(self,*args):
        nr = int(args[1][0])-1
        rows_num = self.data_tables.table_data.rows_num
        pages = nr//rows_num
        index = nr-(pages*rows_num)
        status,titel,check = self.Data[link:= self.Links[nr]]
        if (index*3) not in self.data_tables.table_data.current_selection_check[pages]:
            self.Data[link] = [status,titel,False]
        else:
            self.Data[link] = [status,titel,True]

    def updateRow(self,index:int,link:str,data:tuple):
        status,titel = data
        if status == "Abgeschlossen":
            icon = ("checkbox-marked-circle",[39 / 256, 174 / 256, 96 / 256, 1],f"{status}")
        elif status == "Lädt herunter":
            icon = ("download-circle-outline",[39 / 256, 174 / 256, 96 / 256, 1],f"{status}")
        elif status == "#####":
            icon = link
        elif status in ["Datei existiert bereits", "Übersprungen"]:
            icon = ("checkbox-marked-circle",[4 / 256, 159 / 256, 209 / 256, 1],f"{status}")
        else:
            icon = ("alert-circle",[1,0,0,1],f"{status}")
            if link not in self.Fehler: self.Fehler.append(link)
        self.data_tables.row_data[index]= (f"{index + 1}",icon,titel)

    def initMainData(self):
        self.format = self.root.ids.main.ids.btn.text
        if  self.format == "Audio(mp3)":
            self.only_audio = True
        self.resolution = self.root.ids.main.ids.btn3.text
        self.outpath = self.root.ids.main.ids.textinput.text
        ###Widgets###
        self.btn = self.root.ids.data_tab.ids.btn
        self.btn.text = "Weiter"
        self.btn2 = self.root.ids.data_tab.ids.btn2
        self.btn3 = self.root.ids.data_tab.ids.btn3
        self.label = self.root.ids.data_tab.ids.label
        self.percent = self.root.ids.data_tab.ids.percent
        self.pb_1 = self.root.ids.data_tab.ids.pb_1
        self.percent2 = self.root.ids.data_tab.ids.percent2
        self.pb_2 = self.root.ids.data_tab.ids.pb_2

    def Start(self):
        self.initMainData()
        self.index = 0
        self.pause = False
        self.btn.disabled = True
        t1 = threading.Thread(target=self.Loop_Start)
        t1.daemon = True
        t1.start()

    def Weiter(self):
        self.pause = False
        self.btn.disabled = True
        t1 = threading.Thread(target=self.Loop_Start)
        t1.daemon = True
        t1.start()

    def Pause(self):  # pausiert Counter und Downloads
        self.pause = True
        self.btn.disabled = False
        self.btn2.disabled = True

    def popUp_2(self,titel:str,text:str):
        pop = Popup(title=f"{titel}",
                    content=Label(text=text, text_size=(self.root.width * 0.6, None),
                                  size=self.root.size, halign='left', valign='center'),
                    size_hint=(0.7, 0.25))
        pop.open()

    def print_List(self):
        text = ""
        self.outpath = self.root.ids.main.ids.textinput.text
        try:
            with codecs.open(f"{self.outpath}/Videoliste.txt","w","utf-8") as f:
                for link in self.Links:
                    status,titel,check = self.Data[link]
                    text+= f"{link} {titel}\n"
                f.write(text)

            text = f"Liste gespeichert unter:\n{self.outpath}/Videoliste.txt"
            self.popUp_2("Gespeichert",text)
        except Exception as e:
            text =f"Beim Speichern ist ein Fehler aufgetreten:\n{e}"
            self.popUp_2("Fehler",text)

    def Loop_Start(self):
        if self.changed:
            self.initCheckboxes()
            self.changed = False
        self.timeout = False
        if self.index == len(self.Links):  # Wenn das Ende der Warteschlange erreicht ist
            self.stop_update()
            self.btn.pos_hint = self.btn2.pos_hint = {"x":1.5, "top":0.1}
            self.btn3.pos_hint = {"x":0.4, "top":0.1}
            if self.Fehler != []:
                text = ""
                with codecs.open(f"{self.outpath}/Fehlgeschlagene_Downloads.txt", "w", "utf-8") as f:
                    for link in self.Fehler:
                        status, titel, check = self.Data[link]
                        text += f"{link} {titel}\n"
                    f.write(text)
            return
        self.btn2.disabled = False
        status,title,check = self.Data[link:= self.Links[self.index]]
        if status in ["#####", "Unbekannter Kanalname"]:  # Zeilen Überschrift beibehalten
            return self.Loop_End()
        if title == "Fehler":
            self.Data[link][0] = "Fehler"
            return self.Loop_End()
        if not check:  # Kontrolle ob manuell übersprungen
            self.Data[link][0] = "Übersprungen"
            return self.Loop_End()
        for j in range(6):  # Während der Counter läuft kann pausiert werden
            time.sleep(1.0)
            self.label.text = f"Download beginnt in: {str(5 - j)}s"
            if self.pause:  # Kontrolle ob pausiert
                self.btn.disabled = False
                self.btn2.disabled = True
                break
        self.label.text = ""
        if not self.pause:
            self.btn2.disabled = True
            self.pb_1.value = 0
            if self.only_audio:
                self.percent.text = "Audio wird heruntergeladen: 0 %"
            else:
                self.percent.text = "Video wird heruntergeladen: 0 %"
            self.updateRow(self.index, link, ("Lädt herunter",title))
            t2 = threading.Thread(target= self.Download_Manager,args = [link])
            t2.daemon = True
            t2.start()

    def Loop_End(self):
        status, title, check = self.Data[link := self.Links[self.index]]
        self.pb_1.value = 100
        self.percent.text = "Abgeschlossen"
        self.updateRow(self.index, link, (status, title))
        if not self.timeout:
            self.pb_2.value = int(((self.index+1) / len(self.Links)) * 100)
            self.percent2.text = str(int(((self.index+1) / len(self.Links)) * 100)) + " %"
            self.index += 1
        return self.Loop_Start()

    def Timeout(self):
        self.timeout = True
        self.Data[self.Links[self.index]][0] = "Verbindung verloren"  # neuen Status setzen
        text = "Zeitüberschreitung bei der\nNetzwerkverbindung"
        self.popUp_2("Fehler", text)
        self.Pause()
        return self.Loop_End()

    def Download_Progress(self, chunk, file_handle, bytes_remaining):  # Rechner für Statusanzeige
        percent = (100 * (self.file_size - bytes_remaining)) // self.file_size
        percent = max(0,min(100, percent))
        self.pb_1.value = percent
        if self.only_audio or self.video_downloaded:
            self.percent.text = f"Audio wird heruntergeladen: {percent} %"
        else:
            self.percent.text = f"Video wird heruntergeladen: {percent} %"

    def Download_Manager(self, link):
        for j in range(3):
            try:
                self.youtubeObject = YouTube(link, on_progress_callback=self.Download_Progress)
                title = self.youtubeObject.title
                break
            except:
                continue
        else:
            Clock.schedule_once(lambda dt: self.Timeout(), 0.5)
        for i in ["/", ":", "*", "<", ">", "|", "?", '"', "\\"]:
            title = title.replace(i, "")
        title = title.strip()
        self.video_exists = False
        if self.only_audio:
            t3 = threading.Thread(target=self.Audio_Download,args = [title])
        else:
            t3 = threading.Thread(target=self.Video_Download,args = [title])
        t3.daemon = True
        t3.start()

    def Video_Download(self,title:str):  # Lädt die Video-Datei herunter
        self.video_downloaded = False
        if os.path.exists(f"{self.outpath}/{title}.mp4"):
            self.Data[self.Links[self.index]][0] = "Datei existiert bereits"
            self.video_exists = True
            return self.Loop_End()
        try:
            if self.resolution == "bestmögliche Auflösung":
                video = self.youtubeObject.streams.get_highest_resolution()
            elif self.resolution == "niedrigste Auflösung":
                video = self.youtubeObject.streams.get_lowest_resolution()
            else:
                video = self.youtubeObject.streams.filter(res=self.resolution, file_extension="mp4").first()
                if video == None:
                    video = self.youtubeObject.streams.get_highest_resolution()
            try:
                self.file_size = video.filesize
                video.download(f"{self.outpath}",f"{title}.mp4", timeout=10)
                self.video_downloaded = True
                self.Data[self.Links[self.index]][0] = "Abgeschlossen"
            except:
                os.remove(f"{self.outpath}/{title}.mp4")
                Clock.schedule_once(lambda dt: self.Timeout(), 0.5)
        except Exception as e:
            self.Data[self.Links[self.index]][0] = "Fehler"
            if "age restricted" in str(e):
                self.Data[self.Links[self.index]][0] = "Video ist altersbeschränkt"
        return self.Loop_End()

    def Audio_Download(self,title:str):  # Lädt die Audio-Datei herunter
        if os.path.exists(f"{self.outpath}/{title}.mp3"):
            self.Data[self.Links[self.index]][0] = "Datei existiert bereits"
            return self.Loop_End()
        try:
            audio = self.youtubeObject.streams.filter(only_audio=True).first()
            self.file_size = audio.filesize
            audio.download(f"{self.outpath}",f"{title}.mp3", timeout=10)
            self.Data[self.Links[self.index]][0] = "Abgeschlossen"
            return self.Loop_End()
        except Exception as e:
            if os.path.exists(f"{self.outpath}/{title}.mp3"):
                os.remove(f"{self.outpath}/{title}.mp3")
            if "age restricted" in str(e):
                self.Data[self.Links[self.index]][0] = "Video ist altersbeschränkt"
                return self.Loop_End()
            Clock.schedule_once(lambda dt: self.Timeout(), 0.5)

if __name__ == "__main__":
    Youtube_App().run()

#@TODO
#sd karten pfad hinzufügen