import numpy as np
import matplotlib.pyplot as plt
import random
import time

def gen3Osig(f):
    virtual3O = calcV3O(f)
    data = {"xscale":[], "values": [], "dlen": 2**14, "srate": mapsrat(f), "f": f}
    pos = random.random()*(data["srate"]/data["f"])
    error = np.random.normal(0, 0.01, data["dlen"])
    data["xscale"] = np.linspace(0.0, (2**14)*(1/data["srate"]), 2**14)
    eOsig = 0.5 + 0.5 * np.sin(data["f"] * 2.0 * np.pi * data["xscale"] + pos)
    dOsig = virtual3O * np.sin(data["f"] * 3 * 2.0 * np.pi * data["xscale"] + pos)
    data["values"] = eOsig + dOsig + error
    return data, virtual3O

def mapsrat(f):
    sratelist = [2**16, 2**13, 2**10, 2**6, 2**3, 1]
    freqcaplist = [2**2, 2**5, 2**8, 2**12, 2**15, 2**18]
    for srate,cap in zip(sratelist,freqcaplist):
        if f <= cap:
            return ((125000000)/srate)
            break
    else: return ((125000000)/sratelist[-1])

def calcV3O(f):
    virtual3O =  1/(3*np.log10(f*500+10))
    return virtual3O
