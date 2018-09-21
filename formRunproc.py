#region import
import wx
import wx.lib.anchors as anchors

import wx.grid as gridlib
import psutil
import datetime

from callbackThread import CallbackThread

import sqlite3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, DateTime
#endregion

#region Работа с БД
Base = declarative_base()
Engine = create_engine('sqlite:///dbsqlite.db')  # sqlite:///:memory: (or, sqlite://)

class Snapshot (Base):
    __tablename__ = 'snapshots'
    id = Column(Integer, primary_key=True)
    createddt = Column(DateTime, nullable=False)
    comment = Column(String)
    # Foreign Key from table Process
    #processes = relationship('Process', back_populates="snapshots")

class Process (Base):
    __tablename__ = 'processes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    fullpath = Column(String)
    args = Column(String)
    # Foreign Key in table Process
    snapshot_id = Column(Integer, ForeignKey('snapshots.id'))
    #snapshot = relationship("Snapshot", back_populates="processes")

def saveProcessesToDatabase(procList):
    '''(list(ProcInfo)) -> '''
    connection = Engine.connect()
    Session = sessionmaker(bind=Engine)
    session = Session()

    snap = Snapshot()
    snap.createddt = datetime.datetime.now()#.date()
    snap.comment = str(len(procList))
    session.add(snap)
    session.flush()
    if snap.id == None:
        session.refresh(snap)

    for row in procList:
        proc = Process()
        proc.name = row[0]
        proc.fullpath = row[0]
        proc.args = row[0]
        proc.snapshot_id = snap.id
        session.add(proc)
    session.commit()
    connection.close()
    pass

def createDBStructure():
    conn = sqlite3.connect("dbsqlite.db")  # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `snapshots` ( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `createddt` DATETIME, `comment` TEXT )")
    cursor.execute("CREATE TABLE IF NOT EXISTS `processes` ( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `snapshot_id`  NOT NULL, `name` TEXT, `fullpath` TEXT, `args` TEXT )")
    conn.commit()

#endregion

#region Получить список запущенных процессов

def getRunningProcesses():
    '''() -> list(tuple())'''
    result = list()
    for p in psutil.process_iter():
        p_path = ''
        p_args = ''
        try:
            p_path = psutil.Process(p.pid).cmdline()[0]
        except:
            pass
        try:
            p_args = psutil.Process(p.pid).cmdline()[1]
        except:
            pass
        p = (p.name(), p_path, p_args)
        result.append(p)
    return result

#endregion

#region Отобразить данные в гриде
GRID_DATA = []


class SimpleGrid(gridlib.Grid): ##, mixins.GridAutoEditMixin):
    def __init__(self, parent=None, size=None, **kwargs):
        gridlib.Grid.__init__(self, parent=parent, id=-1, size=size)

        #self.grid_data = []

        columns_names = list(kwargs["column_names"])
        default_rowcount = int(kwargs["default_rowcount"])

        self.CreateGrid(default_rowcount, len(columns_names))  # , gridlib.Grid.SelectRows)
        for i in range(len(columns_names)):
            self.SetColLabelValue(i, columns_names[i])
            self.SetColSize(i, 250)

        self.rebind_in_thread()

    def rebind_in_thread(self):
        self.bisy_gauge = wx.Gauge(self, -1, 50, (110, 50), (250, -1))
        self.bisy_gauge.CenterOnParent()
        self.bisy_gauge.Pulse()

        thread = CallbackThread(
            name='get_running_processes',
            target=grid_thread_job,
            callback=grid_thread_callback,
            callback_args=(self, '')
            )
        thread.start()

def grid_thread_job():
    global GRID_DATA
    GRID_DATA = getRunningProcesses()

def grid_thread_callback(grid: SimpleGrid, param1: str):
    global GRID_DATA
    curr_row_count = grid.GetNumberRows()
    data_len = len(GRID_DATA)
    if curr_row_count < data_len:
        grid.AppendRows(data_len - curr_row_count)
    elif curr_row_count > data_len:
        grid.DeleteRows(0, curr_row_count-data_len)
    curr_row_count = grid.GetNumberRows()

    grid.AppendRows(1)

    row = 0
    for p in GRID_DATA:
        grid.SetCellValue(row, 0, p[0])
        grid.SetCellValue(row, 1, p[1])
        grid.SetCellValue(row, 2, p[2])
        row += 1

    grid.bisy_gauge.Destroy()

#endregion

[ID_SAVEDBBUTTON, ID_REBINDBUTTON, ID_OKBUTTON] = wx.NewIdRef(3)

class FormRunproc(wx.MDIChildFrame):
    def __init__(self, parent, title):
        wx.MDIChildFrame.__init__(self, parent, title=title)#, style=wx.MAXIMIZE)

        self.mainPanel = wx.Panel(parent=self, name='panel1', style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN | wx.FULL_REPAINT_ON_RESIZE, pos=(0, 0), size=self.Size)
        #self.mainPanel = self
        self.mainPanel.SetAutoLayout(True)

        self.grid = SimpleGrid(self.mainPanel, (self.Size.x, self.Size.y-24), column_names=["Process name", "Path", "Argumens"], default_rowcount=0)
        self.grid.SetConstraints(anchors.LayoutAnchors(self.grid, True, True, True, True))
        # Кнопка
        self.rebindButton = wx.Button(label='Refresh', id=ID_REBINDBUTTON,  parent=self.mainPanel, name='rebindButton', size=(72, 24), style=0, pos=(0, self.Size.y - 24))
        self.rebindButton.SetConstraints(anchors.LayoutAnchors(self.rebindButton, True, False, False, True))
        self.Bind(wx.EVT_BUTTON, self.OnRebindButtonClick, id=ID_REBINDBUTTON)
        # Кнопка
        self.savedbButton = wx.Button(label='Save to DB', id=ID_SAVEDBBUTTON,  parent=self.mainPanel, name='savedbButton', size=(72, 24), style=0, pos=(72, self.Size.y - 24))
        self.savedbButton.SetConstraints(anchors.LayoutAnchors(self.savedbButton, True, False, False, True))
        self.Bind(wx.EVT_BUTTON, self.OnSavedbButtonClick, id=ID_SAVEDBBUTTON)
        #Кнопка
        self.okButton = wx.Button(label='OK', id=ID_OKBUTTON,  parent=self.mainPanel, name='okButton', size=(72, 24), style=0, pos=(self.Size.x - 72, self.Size.y - 24))
        self.okButton.SetConstraints(anchors.LayoutAnchors(self.okButton, False, False, True, True))
        self.Bind(wx.EVT_BUTTON, self.OnOkButtonClick, id=ID_OKBUTTON)

    def OnRebindButtonClick(self, event):
        self.grid.rebind_in_thread()

    def OnSavedbButtonClick(self, event):
        createDBStructure()
        global GRID_DATA
        saveProcessesToDatabase(GRID_DATA)


    def OnOkButtonClick(self, event):
        self.Close()


# class MyApp(wx.App):
#     def OnInit(self):
#         frame = wx.Frame()
#         frame.grid = SimpleGrid(frame)
#         frame.Show(True)
#         self.SetTopWindow(frame)
#         return True
#
# if __name__ == '__main__':
#     app = MyApp(False)
#     app.MainLoop()