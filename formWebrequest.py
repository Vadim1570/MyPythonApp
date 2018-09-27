import wx
import wx.lib.anchors as anchors
import requests
import datetime
import wx.html as html

class myRequests:
    def getWeateher(self):
        #site:    openweathermap.org
        #user:    e509
        #email:   e5095237@nwytg.net
        #password bEcA5aYCh3AZfyZ
        key="6c0938395c09deee87b214a50c329c35"
        cityId = "1490624" #Surgut
        url = "http://api.openweathermap.org/data/2.5/weather?id={0}&APPID={1}".format(cityId, key)
        headers = {'content-type': 'text/xml'}
        body = ""
        response = requests.post(url,data=body,headers=headers)
        return response.content

    def getTime(self):
        #site:    timezonedb.com
        #user:    ariyana.neely
        #email:   ariyana.neely@0n0ff.net
        #password bEcA5aYCh3AZfyZ
        #http://timezonedb.com/activate?user=ariyana.neely&code=c93f254cad
        #Username: ariyana.neely
        #API Key: S23QZQWXSEEP
        url="http://api.timezonedb.com/v2.1/list-time-zone?key=S23QZQWXSEEP&format=json&country=RU"
        headers = {'content-type': 'text/xml'}
        body = ""
        response = requests.post(url,data=body,headers=headers)
        return response.content

    def getCurrency(self):
        #http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?op=GetCursOnDate"
        url="http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
        #headers = {'Content-Type': 'application/soap+xml'}
        headers = {'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': '"http://web.cbr.ru/GetCursOnDate"'}
        dateTime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') # AllXsd format '2018-09-27T15:00:00'
        #region strftime help
        # %a  Locale’s abbreviated weekday name.
        # %A  Locale’s full weekday name.
        # %b  Locale’s abbreviated month name.
        # %B  Locale’s full month name.
        # %c  Locale’s appropriate date and time representation.
        # %d  Day of the month as a decimal number [01,31].
        # %f  Microsecond as a decimal number [0,999999], zero-padded on the left
        # %H  Hour (24-hour clock) as a decimal number [00,23].
        # %I  Hour (12-hour clock) as a decimal number [01,12].
        # %j  Day of the year as a decimal number [001,366].
        # %m  Month as a decimal number [01,12].
        # %M  Minute as a decimal number [00,59].
        # %p  Locale’s equivalent of either AM or PM.
        # %S  Second as a decimal number [00,61].
        # %U  Week number of the year (Sunday as the first day of the week)
        # %w  Weekday as a decimal number [0(Sunday),6].
        # %W  Week number of the year (Monday as the first day of the week)
        # %x  Locale’s appropriate date representation.
        # %X  Locale’s appropriate time representation.
        # %y  Year without century as a decimal number [00,99].
        # %Y  Year with century as a decimal number.
        # %z  UTC offset in the form +HHMM or -HHMM.
        # %Z  Time zone name (empty string if the object is naive).
        # %%  A literal '%' character.
        #endregion
        body = """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <GetCursOnDate xmlns="http://web.cbr.ru/">
            <On_date>{0}</On_date>
            </GetCursOnDate>
        </soap:Body>
        </soap:Envelope>""".format(dateTime)
        headers['Content-Length'] = (str)(len(body))
        response = requests.post(url,data=body,headers=headers)
        return response.content


[ID_REQBUTTON1, ID_REQBUTTON2, ID_REQBUTTON3, ID_OKBUTTON] = wx.NewIdRef(4)

class FormWebrequest(wx.MDIChildFrame):
    def __init__(self, parent, title):
        wx.MDIChildFrame.__init__(self, parent, title=title)

        self.mainPanel = wx.Panel(parent=self, name='panel1', style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN | wx.FULL_REPAINT_ON_RESIZE, pos=(0, 0), size=self.Size)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        fgs = wx.FlexGridSizer(3, 3, 10, 10)

        label1 = wx.StaticText(self.mainPanel, label="Weather")
        label2 = wx.StaticText(self.mainPanel, label="Time")
        label3 = wx.StaticText(self.mainPanel, label="Currency")
        button1 = wx.Button(self.mainPanel, ID_REQBUTTON1, u"Show Weather", wx.DefaultPosition, wx.DefaultSize, 0)
        button2 = wx.Button(self.mainPanel, ID_REQBUTTON2, u"Show Time", wx.DefaultPosition, wx.DefaultSize, 0)
        button3 = wx.Button(self.mainPanel, ID_REQBUTTON3, u"Show Currency", wx.DefaultPosition, wx.DefaultSize, 0)
        self.Bind(wx.EVT_BUTTON, self.OnbtnRequest1Click, id=ID_REQBUTTON1)
        self.Bind(wx.EVT_BUTTON, self.OnbtnRequest2Click, id=ID_REQBUTTON2)
        self.Bind(wx.EVT_BUTTON, self.OnbtnRequest3Click, id=ID_REQBUTTON3)

        self.textbox1 = wx.TextCtrl(self.mainPanel, style=wx.TE_MULTILINE, size=(100, 100))
        self.textbox2 = wx.TextCtrl(self.mainPanel, style=wx.TE_MULTILINE, size=(100, 100))
        self.textbox3 = wx.TextCtrl(self.mainPanel, style=wx.TE_MULTILINE, size=(100, 100))

        fgs.AddMany([(label1), button1, (self.textbox1, 1, wx.EXPAND),
                     (label2), button2, (self.textbox2, 1, wx.EXPAND),
                     (label3, 1, wx.EXPAND), button3, (self.textbox3, 1, wx.EXPAND)
                     ])
        fgs.AddGrowableRow(2, 1)
        fgs.AddGrowableCol(2, 1)
        hbox.Add(fgs, proportion=3, flag=wx.ALL | wx.EXPAND, border=15)
        self.mainPanel.SetSizer(hbox)

        pass
    
    def OnbtnRequest1Click(self, event):
        resp = myRequests.getWeateher(self)
        self.textbox1.write(resp)

    def OnbtnRequest2Click(self, event):
        resp = myRequests.getTime(self)
        self.textbox2.write(resp)

    def OnbtnRequest3Click(self, event):
        resp = myRequests.getCurrency(self)
        self.textbox3.write(resp)