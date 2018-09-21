import wx
import wx.grid as gridlib
from threading import Thread
from winreg import OpenKey, CloseKey, QueryInfoKey, EnumKey, EnumValue, QueryValue, HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, HKEY_USERS

#region Список запущенных программ

mapping = {HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE", HKEY_CURRENT_USER: "HKEY_CURRENT_USER", HKEY_USERS: "HKEY_USERS"}

def GetInstalledPrograms ():
    result = list()
    regPaths = (
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",             #HKEY_LOCAL_MACHINE #HKEY_CURRENT_USER
        r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall",  #HKEY_LOCAL_MACHINE
    )
    for HKEY_ID in (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER):
        for path in regPaths:
            try:
                subKeys = readSubKeys(HKEY_ID, path)
                for regKeyName in subKeys:
                    regValues = readValues(HKEY_ID, "{0}\{1}".format(path, regKeyName))

                    DisplayName = ''
                    DisplayVersion = ''
                    Publisher = ''
                    InstallDate = ''
                    InstallLocation = ''
                    DefaultValue = regKeyName
                    RegBranch = "{0}\{1}\{2}".format(mapping[HKEY_ID], path, regKeyName)

                    for k, v in regValues.items():
                        if k == "DisplayName": DisplayName = str(v)
                        if k == "DisplayVersion": DisplayVersion = str(v)
                        if k == "Publisher": Publisher = str(v)
                        if k == "InstallDate": InstallDate = str(v)
                        if k == "InstallLocation": InstallLocation = str(v)
                        #DefaultValue = str(v)

                    if DisplayName == '': DisplayName = DefaultValue

                    result.append((DisplayName, DisplayVersion, Publisher, InstallDate, InstallLocation, RegBranch))

                break
            except OSError:
                pass
    return result

def pathExists(hkey, regPath):
    try:
        reg = OpenKey(hkey, regPath)
    except WindowsError:
        return False
    CloseKey(reg)
    return True

def readSubKeys(hkey, regPath):
    if not pathExists(hkey, regPath):
        return -1
    reg = OpenKey(hkey, regPath)
    subKeys = []
    noOfSubkeys = QueryInfoKey(reg)[0]
    for i in range(0, noOfSubkeys):
        subKeys.append(EnumKey(reg, i))
    CloseKey(reg)
    return subKeys

def readValues(hkey, regPath):
    if not pathExists(hkey, regPath):
        return -1
    reg = OpenKey(hkey, regPath)
    values = {}
    noOfValues = QueryInfoKey(reg)[1]
    for i in range(0, noOfValues):
        values[EnumValue(reg, i)[0]] = EnumValue(reg, i)[1]
    CloseKey(reg)
    return values

#endregion

#region Получение данных в потоке

#endregion

#region Рисуем таблицу

class SimpleGrid(gridlib.Grid): ##, mixins.GridAutoEditMixin):
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1)
        ##mixins.GridAutoEditMixin.__init__(self)

        self.moveTo = None

        #self.Bind(wx.EVT_IDLE, self.OnIdle)

        grid_data = GetInstalledPrograms()

        self.CreateGrid(len(grid_data), 6)#, gridlib.Grid.SelectRows)
        ##self.EnableEditing(False)

        self.SetColLabelValue(0, "DisplayName")
        self.SetColLabelValue(1, "DisplayVersion")
        self.SetColLabelValue(2, "Publisher")
        self.SetColLabelValue(3, "InstallDate")
        self.SetColLabelValue(4, "InstallLocation")
        self.SetColLabelValue(5, "RegBranch")

        row = 0
        for p in grid_data:
            self.SetCellValue(row, 0, p[0])
            self.SetCellValue(row, 1, p[1])
            self.SetCellValue(row, 2, p[2])
            self.SetCellValue(row, 3, p[3])
            self.SetCellValue(row, 4, p[4])
            self.SetCellValue(row, 5, p[5])
            row += 1

    def OnIdle(self, evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None

        evt.Skip()
#endregion

class FormInsprogs(wx.MDIChildFrame):
    def __init__(self, parent, title):
        wx.MDIChildFrame.__init__(self, parent, title=title)
        self.grid = SimpleGrid(self)
        pass