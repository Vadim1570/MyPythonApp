""""""
import psutil
import csv
import os


import subprocess
from dataclasses import dataclass
import sqlite3

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

#region Database sqlalchemy

Base = declarative_base()
Engine = create_engine('sqlite:///dbsqlite.db')  # sqlite:///:memory: (or, sqlite://)

class Process1 (Base):
    __tablename__ = 'processes1'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    fullpath = Column(String)
    args = Column(String)
    # Foreign Key from table processes2
    # proc2 = relationship('Process2', back_populates="processes1")


class Process2 (Base):
    __tablename__ = 'processes2'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    fullpath = Column(String)
    args = Column(String)
    # Foreign Key in table processes2
    # proc1_id = Column(Integer, ForeignKey('processes1.id'))
    # proc1 = relationship("Process1", back_populates="processes2")

def insertProcesses1(procInfoList):
    '''(list(ProcInfo)) -> '''
    connection = Engine.connect()
    Session = sessionmaker(bind=Engine)
    session = Session()
    #DELETE ALL
    session.query(Process1).delete()
    session.commit()

    # for p in procInfoList:
    #     p1 = Process1()
    #     p1.name = p.name
    #     p1.fullpath = p.path
    #     p1.args = p.args
    #     session.add(p1)
    # session.commit()
    connection.close()
    pass

#endregion

#region Database sqlite3

def createDatabase():
    conn = sqlite3.connect("dbsqlite.db")  # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `processes1` ( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `name` TEXT, `fullpath` TEXT, `args` TEXT )")
    cursor.execute("CREATE TABLE IF NOT EXISTS `processes2` ( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `name` TEXT, `fullpath` TEXT, `args` TEXT )")
    conn.commit()

def insertProcInfoIntoDB(procInfoList, tablename):
    '''(list(ProcInfo), str) -> '''
    conn = sqlite3.connect("dbsqlite.db")  # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()
    cursor.execute("DELETE FROM {0}".format(tablename))
    #for p in procInfoTuple:
        #cursor.execute("INSERT INTO {0} VALUES (null, '?', '?', '?')".format(tablename), (p[0], p[1], p[2]))
        #cursor.execute("INSERT INTO {0} VALUES (null, ':name', ':fullpath', ':args')".format(tablename), {"name":p[0], "fullpath":p[1], "args":p[2]})
    #    cursor.execute("INSERT INTO {0} VALUES (null, '{1}', '{2}', '{3}')".format(tablename, p[0], p[1], p[2]))
    #    conn.commit()
    procInfoTuple = [p.asTuple() for p in procInfoList]
    cursor.executemany("INSERT INTO {0} VALUES (null, ?,?,?)".format(tablename), procInfoTuple)
    conn.commit()
    pass

#endregion

#region OS processes
def getProcInfoList():
    '''() -> list(tuple())'''
    result = list()
    for p in psutil.process_iter():
        p_path = ''
        p_args = ''
        try:
            p_path = psutil.Process(p.pid).cmdline()[0]
        except:
            pass;
        try:
            p_args = psutil.Process(p.pid).cmdline()[1]
        except:
            pass;
        p = ProcInfo(p.name(), p_path, p_args)
        result.append(p)
    return result

#@dataclass
class ProcInfo:
    name = ''; path = ''; args = ''
    def __init__(self, name, path, args): self.name = name; self.path = path; self.args = args
    def __hash__(self): return hash(self.name+self.path+self.args)
    def __repr__(self): return '{0}\t{1}\t{2}\n'.format(self.name, self.path, self.args)
    def asDict(self): return {"name": self.name, "path": self.path, "args": self.args}
    def asTuple(self): return (self.name, self.path, self.args)

#endregion

#region Пример работы с реестром
from winreg import OpenKey, CloseKey, QueryInfoKey, EnumKey, EnumValue, QueryValue, HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, HKEY_USERS
mapping = { HKEY_LOCAL_MACHINE : "HKEY_LOCAL_MACHINE", HKEY_CURRENT_USER : "HKEY_CURRENT_USER", HKEY_USERS:"HKEY_USERS" }

def GetProgramInstalledInfo (progName):
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
                    for k,v in regValues.items():
                        if k == "DisplayName":
                            findIndex = 1#str(v).find(progName)
                            if findIndex > 0:
                                print (mapping[HKEY_ID]+' '+path, regKeyName, k, str(v))
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

class Main:
    def __init__(self): pass
    def __del__(self): pass
    def run(self):
        print("Введите одну из команд:")
        print("1 - Записать список запущенных процессов в файл 1.txt")
        print("2 - Записать список запущенных процессов в файл 2.txt")
        print("3 - Сравнить файлы 1 и 2 и записать результат в 3.txt")
        print("4 - Открыть папку с файлами")
        print("0 - Выход")
        cmd = input()
        while cmd != '0':
            if cmd == '1':
                #with open('1.txt', "w", newline="") as file:
                #    writer = csv.DictWriter(file, fieldnames=['name', 'path', 'args'])
                #    writer.writeheader()
                #    processes = [p.asDict() for p in getProcInfoList()]
                #    writer.writerows(processes)
                #insertProcInfoIntoDB(getProcInfoList(), "processes1")
                insertProcesses1(getProcInfoList())
            elif cmd == '2':
                #with open('2.txt', "w", newline="") as file:
                #    writer = csv.DictWriter(file, fieldnames=['name', 'path', 'args'])
                #    writer.writeheader()
                #    processes = [p.asDict() for p in getProcInfoList()]
                #    writer.writerows(processes)
                insertProcInfoIntoDB(getProcInfoList(), "processes2")

            elif cmd == '3':
                pass
                """          
                list1 = set()
                list2 = set()
                with open('1.txt', "r", newline="") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        list1.add(ProcInfo(row['name'], row['path'], row['args']))
                with open('2.txt', "r", newline="") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        list2.add(ProcInfo(row['name'], row['path'], row['args']))
                list12 = list1 - list2
                list21 = list2 - list1
                list12 = [str(p) for p in list12]
                list21 = [str(p) for p in list21]
                with open("3.txt", "w") as file:
                    file.write("Процессы, входящие в 1.txt, но не входящие в 2.txt\n")
                    file.writelines(list12)
                    file.write("Процессы, входящие в 2.txt, но не входящие в 1.txt\n")
                    file.writelines(list21)
                """
            elif cmd == '4':
                dir = os.path.abspath(os.curdir)
                subprocess.Popen('explorer "{0}"'.format(dir))
            elif cmd == '5':
                createDatabase()
            else:
                print("Команда не распознана")

            print("Введите следующую команду:")
            cmd = input()

print(__name__)

Main().run()
#for s in GetProgramInstalledInfo ("MSYS2"): print(s)