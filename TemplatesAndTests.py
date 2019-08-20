"""
Usefull functions for loading files etc.
-AN
"""

import os
import pickle
import zipfile, lzma
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
# saves dict to csv using keys as headers
def saveToCSV(savedict, filename = "", path = ""):
    try:
        #print(savedict)
        if not filename:
            datanum = 1
            filename = "data"
            while os.path.isfile("".join([filename,str(datanum),".csv"])):
                datanum += 1
            filename = "".join([filename,str(datanum)])
        if filename[-4:] != ".csv":
            filename = "".join([filename,".csv"])
        if not os.path.isdir(path):
            os.makedirs(path)
        if not os.path.isfile("".join([path,filename])):
            file = open("".join([path,filename]),'w')
            file.write("".join([";".join(list(savedict.keys())),";\n"]))
            file.close()
        file = open("".join([path,filename]),'a')
        valueslist = list(savedict.values())
        for rowcount in range((len(list(valueslist[0])))):
            for values in valueslist:
                file.write("".join([str(values[rowcount]), ";"]))
            file.write(";\n")
    except PermissionError:
        print("Error saving data, is the file open?")
    except (AttributeError, TypeError):
        print("Error in dataformat, use a dict filled with lists.")
    except KeyError:
        print("Error in length of data")
    return 1


# takes a dict and gives a list with dicts. Kinda sorts by relKey
def splitIntoDicts(data, relKey="Lackh (m)"):
    dicts = []
    for group in set(data[relKey]):
        datanew = OrderedDict()
        for gnumb, gline in enumerate(data[relKey]):
            if gline == group:
                for key in data:
                    if key in datanew:
                        datanew[key].append(data[key][gnumb])
                    else:
                        datanew[key] = [data[key][gnumb]]
        dicts.append(datanew)
    return dicts


def parseSubDirs(filtlistlist, dirname=""):
    """
    :param filtlistlist: list of lists of strings
    :param dirname: dir to start parsing from added to cwd
    :return: list of all files containing at least one of the string of all the lists in filtlistlist
    """
    path = os.getcwd() + "//" + dirname
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            for filtlist in filtlistlist:
                if not np.any([filt in os.path.join(r, file) for filt in filtlist]):
                    break
            else:
                files.append(os.path.join(r, file))
    return files

def multiReadData(paths, filtlist, splitString="Frequenz [Hz]"):
    dataDict = OrderedDict()
    for path in paths:
        data, metadata = readData(path)
        filename = path.split("\\")[-1]
        if splitString not in data:
            splitString = "frequenz (Hz)"  # in case you spelled it wrong
        data = splitData(data, splitString)
        for filtkey in filtlist:
            if filtkey in path:
                if not filtkey in dataDict:
                    dataDict[filtkey] = OrderedDict()
                if not filename in dataDict[filtkey]:
                    dataDict[filtkey][filename] = OrderedDict()
                dataDict[filtkey][filename]["data"] = data
                dataDict[filtkey][filename]["metadata"] = metadata
                dataDict[filtkey][filename]["metadata"]["path"] = path
    return dataDict


def splitData(data, relKey = "Frequenz [Hz]"):
    """
    :param data:
        dictionary with data
    :return:
        data separated into sweeps
    """
    print(data.keys())
    if relKey in data:
        relKey = relKey
    elif "frequenz (Hz)" in data:
        relKey = "frequenz (Hz)"
    elif 'Frequenz [Hz]' in data:
        relKey = 'Frequenz [Hz]'
    newdict = OrderedDict()
    sweepAm = 0
    if len(set(data[relKey])) == len(data[relKey]):
        for key in data:
            newdict[key] = [data[key]]
        return newdict
    cor = -(data[relKey][0]-data[relKey][1])/np.abs(data[relKey][0]-data[relKey][1])
    for point, el in enumerate(data[relKey]):
        if (point > 0 and (el*cor) < (data[relKey][point-1])*cor) or (point == len(data[relKey])-cor):
            for key in data:
                if key in newdict:
                    newdict[key].append(data[key][sweepAm:point])
                else:
                    newdict[key] = [data[key][sweepAm:point]]
            sweepAm=point
    return newdict

def savePickle(savedict, filename = "", path =""):
    datanum = 1
    while os.path.isfile(path+str(datanum)+".pkl"):
        datanum += 1
    filename = "".join([filename,str(datanum)])
    if filename[-4:] != ".pkl":
        filename = "".join([filename,".pkl"])
    if not os.path.isdir(path):
        os.makedirs(path)
    with open("".join([path,filename]), 'wb+') as rawF:
        pickle.dump(savedict, rawF, pickle.HIGHEST_PROTOCOL)


def winAvg(data, winWidth=0, winfunc=np.blackman, mode="same"):
    if not winWidth:
        if int(len(data)*(5/100)) > 0:
            winWidth = int(len(data)*(10/100))
        else: return data
    kernel = winfunc(winWidth)/np.sum(winfunc(winWidth))
    data = np.convolve(data, kernel, mode=mode)
    return data


# zips raw data of all sub folders to path containing the provided string
def zipRaw(path = os.getcwd(), mark="_raw", outname = "raw.zip"):
    if outname[-4:] != ".zip":
        outname = "".join([outname,".zip"])
    zf = zipfile.ZipFile(outname, mode="w")
    cTree = list(os.walk(path))
    for folder in cTree[0][1]:
        if mark in folder:
            for datei in list(os.walk(path+ "//" +folder))[0][2]:
                zf.write(folder+"//"+datei, compress_type=zipfile.ZIP_LZMA)
    zf.close()
    return 1


def readData(filename, path=""):
    """
    :param filename: trivial
    :param path: trivial
    :return: data, metadata as dicts
    """
    data = dict()
    metadata = dict()
    with open("".join([path, filename]),'r') as file:
        lines = [[part for part in line.rstrip('\n').split(";") if part] for line in file]
        for count,line in enumerate(lines):
            if len(line) > 3:
                keyline = line
                keypoint = count
                break
            if len(line) == 2 or not line[0]:
                metadata[str(line[0])] = str(line[1])
        for key in keyline:
            data[key] = []
        for line in lines:
            if len(line) == len(data.keys()):
                for pos in range(len(keyline)):
                    try:
                        data[keyline[pos]].append(float(line[pos]))
                    except: pass

    metadata["dataKeys"] = data.keys()
    return data, metadata


if __name__ == "__main__":
    testdict = {"temperature": [1,2,3,4], "length":[4,5,6,7], "time":[8,9,10,11]}
    data,metadata = readData("Daten_sim.csv", path="/home/an/01_XSensor/Chipvergleich/")
    data = splitData(data)
    signal = {"values": data["UBol (V), Spannung"]}
    print(np.shape(signal["values"]))
    plt.plot(signal["values"][0])
    plt.show()