from datetime import datetime as dt
from datetime import timedelta
from os import listdir, mkdir
from time import sleep
import json
import threading
import wx

class BBWin(wx.Frame):
    def __init__(self, parent, title):
        super(BBWin, self).__init__(parent, title=title, size=(800,800), style=wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        #STARTUP
        if "local" not in listdir():
            mkdir("local")
        if "events.json" not in listdir("local"):
            with open("global/events_template.json") as f:
                template = json.loads(f.read())
            for header in list(template.keys()):
                for k in list(template[header].keys()):
                    template[header][k]['done'] = dt.now().timetuple()
            with open("local/events.json", 'w') as f:
                f.write(json.dumps(template))
        if "settings.json" not in listdir("local"):
             with open("global/settings_template.json") as f:
                template = json.loads(f.read())
             with open("local/settings.json", 'w') as f:
                 f.write(json.dumps(template))
        with open("local/events.json") as f:
            self.events = json.loads(f.read())
        for header in list(self.events.keys()):
            for k in list(self.events[header].keys()):
                if k != "MEASURE" and k != "VICIOUS_BEE_COOLDOWN":
                    self.events[header][k]['done'] = dt(*self.events[header][k]['done'][0:6]) #converts the timetuple back to dt object
        with open("local/settings.json") as f:
            self.settings = json.loads(f.read())

        self.InitUI()
        self.thBBclock = threading.Thread(target=self.BBClockUpdate, daemon=True)
        self.thBBclock.start()

    def InitUI(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(54, 57, 63))
        fBody = wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, False, "Raleway", wx.FONTENCODING_DEFAULT)
        fTitle = wx.Font(25, wx.MODERN, wx.NORMAL, wx.BOLD, False, "Fugaz One", wx.FONTENCODING_DEFAULT)

        #TITLES
        self.tDispenserTitle = wx.StaticText(panel, label="Dispensers", pos=(10,0), size=(360,40), style=wx.ST_NO_AUTORESIZE)
        self.tBeesmasTitle = wx.StaticText(panel, label="Beesmas", pos=(10,250), size=(360,40), style=wx.ST_NO_AUTORESIZE)
        self.tCondDispTitle = wx.StaticText(panel, label="Cond. Disp.", pos=(10,570), size=(360,40), style=wx.ST_NO_AUTORESIZE)
        self.tMobsTitle = wx.StaticText(panel, label="Mobs", pos=(400,0), size=(360,40), style=wx.ST_NO_AUTORESIZE)
        self.tBossesTitle = wx.StaticText(panel, label="Bosses", pos=(400,220), size=(360,40), style=wx.ST_NO_AUTORESIZE)
        self.tMemMatchTitle = wx.StaticText(panel, label="Memory Match", pos=(400,390), size=(360,40), style=wx.ST_NO_AUTORESIZE)
        self.tSummonersTitle = wx.StaticText(panel, label="Summoners", pos=(400,570), size=(360,40), style=wx.ST_NO_AUTORESIZE)
        #Set all headers to specific formatting (I hate CSS but this is making me miss CSS)
        headerText = [self.tDispenserTitle, self.tBeesmasTitle, self.tCondDispTitle, self.tMobsTitle, self.tBossesTitle, self.tMemMatchTitle, self.tSummonersTitle]
        for t in headerText:
            t.SetFont(fTitle)
            t.SetForegroundColour((237, 237, 237))

        #GUI GENERATION
        self.timers = {c: {e: {} for e in list(self.events[c].keys())} for c in list(self.events.keys())} #big dict
        print(self.timers)
        for category in list(self.events.keys()):
            if category == "Dispensers":
                baseXval = 10
                baseYval = 40
            elif category == "Beesmas":
                baseXval = 10
                baseYval = 290
            elif category == "Conditional Dispenser":
                baseXval = 10
                baseYval = 610
            elif category == "Mobs":
                baseXval = 400
                baseYval = 40
            elif category == "Bosses":
                baseXval = 400
                baseYval = 260
            elif category == "Memory Match":
                baseXval = 400
                baseYval = 430
            elif category == "Summoners":
                baseXval = 400
                baseYval = 610

            for event in list(self.events[category].keys()):
                self.timers[category][event] = {"Image": wx.StaticBitmap(panel, -1, wx.Bitmap(f"global/img/{event}.png", wx.BITMAP_TYPE_ANY), (baseXval,baseYval), (30,30)), "Title": wx.StaticText(panel, label=event, pos=(baseXval+40,baseYval), size=(160,30), style=wx.ST_NO_AUTORESIZE), "Time": wx.StaticText(panel, label="", pos=(baseXval+200,baseYval), size=(100,30), style=wx.ST_NO_AUTORESIZE), "Reset": wx.BitmapButton(panel, -1, wx.Bitmap("global/img/refresh.png", wx.BITMAP_TYPE_ANY), pos=(baseXval+330,baseYval), size=(30,30))}
                self.Bind(wx.EVT_BUTTON, lambda e, tempCategory=category, tempEvent=event: self.ResetTime(e, tempCategory, tempEvent), self.timers[category][event]["Reset"]) #the reason temp is passed the way it is instead of just category/events is because... python shenanigans. Here are the sources as to why:
                #https://stackoverflow.com/questions/25393119/in-wxpython-how-do-i-bind-to-separate-objects-in-a-loop-including-arguments
                #https://docs.python-guide.org/writing/gotchas/#late-binding-closures
                self.timers[category][event]["Title"].SetFont(fBody)
                self.timers[category][event]["Title"].SetForegroundColour((237, 237, 237))
                self.timers[category][event]["Time"].SetFont(fBody)
                self.timers[category][event]["Time"].SetForegroundColour((237, 237, 237))
                #DEBUG
                #print(category,': ',baseYval)
                #END DEBUG
                baseYval+=30
                
    def BBClockUpdate(self):
        while True:
            for category in list(self.timers.keys()):
                for event in list(self.timers[category].keys()):
                    if event == "MEASURE" or event == "VICIOUS_BEE_COOLDOWN":
                        continue
                    #print(self.events[category][event]['done'])
                    td = self.events[category][event]['done']-dt.now()
                    tdStr = ""
                    tdHours = td.days*24 + int(td.seconds/3600)
                    if tdHours < 10 and tdHours > 0: 
                        tdStr+=f"0{tdHours}:"
                    elif tdHours >= 10:
                        tdStr+=f"{tdHours}:"
                    tdMinutes = int(td.seconds%3600/60)
                    if tdMinutes < 10 or tdMinutes == 0: 
                        tdStr+=f"0{tdMinutes}:"
                    elif tdMinutes >= 10:
                        tdStr+=f"{tdMinutes}:"
                    tdSeconds = int(td.seconds%3600%60)
                    if tdSeconds < 10 or tdMinutes == 0: 
                        tdStr+=f"0{tdSeconds}"
                    elif tdSeconds >= 10:
                        tdStr+=f"{tdSeconds}"
                    if self.events[category][event]['done'] <= dt.now():
                        self.timers[category][event]["Time"].SetLabel("Ready!")
                    else:
                        self.timers[category][event]["Time"].SetLabel(tdStr)
                        #self.timers[category][event]["Time"].SetLabel(f"{tdHours}:{tdMinutes}:{tdSeconds}")

            #self.tAntPassTitle.SetLabel(f"Ant Pass - {self.events['Dispenser']['Ant Pass']['done'].strftime('%m/%d %H:%M:%S')}")
            #antPassDelta = self.events['Dispenser']['Ant Pass']['done']-dt.now()
            #apHours = antPassDelta.days*24 + int(antPassDelta.seconds/3600)
            #apMinutes = int(antPassDelta.seconds%3600/60)
            #apSeconds = int(antPassDelta.seconds%3600%60)
            #self.tAntPassTitle.SetLabel(f"Ant Pass - {apHours}h{apMinutes}m{apSeconds}s")
            sleep(1)

    def ResetTime(self, e, category, timer):
        print(category,timer)
        cooldown = self.events[category][timer]['cooldown']
        if (category == "Mobs" or category == "Bosses") and self.settings["hasGiftedVicious"]:
            cooldown*=.85 #Gifted Vicious Bee cooldown
        if category == "Mobs":
            self.events[category][timer]['done'] = dt.now() + timedelta(minutes=cooldown)
        else:
            self.events[category][timer]['done'] = dt.now() + timedelta(hours=cooldown)

    def OnClose(self, e):
        #Shutdown/save stuff here
        self.events_jsonable = self.events
        for header in list(self.events_jsonable.keys()):
            for k in list(self.events_jsonable[header].keys()):
                if k != "MEASURE" and k != "VICIOUS_BEE_COOLDOWN":
                    self.events_jsonable[header][k]['done'] = self.events_jsonable[header][k]['done'].timetuple() #timetuple turns the dt object into a tuple so it can be saved in the json
        with open("local/events.json", 'w') as f:
            f.write(json.dumps(self.events_jsonable))
        self.Destroy()

def main():
    app = wx.App()
    ex = BBWin(None, title="BusyBee - v1.0")
    ex.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()