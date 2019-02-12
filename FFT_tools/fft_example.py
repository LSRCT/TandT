import numpy as np
import matplotlib.pyplot as plt
import signalGen


def cutandzeropad(signal, pot = 15):
    A = int((2**14)/(signal["srate"]/signal["f"]))
    signal["dlen"] = int(A*((signal["srate"]/signal["f"])))
    signal["values"] = signal["values"][0:signal["dlen"]]
    signal["xscale"] = signal["xscale"][0:signal["dlen"]]
    # signal["xscale"] = np.linspace(0,(2**pot)/setupdata["srate"],2**pot)
    # zerolist = np.zeros(int(((2**pot)-signal["dlen"])/2))
    # signal["values"] = np.concatenate((zerolist, signal["values"], zerolist))
    # signal["dlen"] = 2**pot
    return signal


# takes a signal dict contaning ["values"], ["srate"], ["dlen"], ["f"] and calculates the 3O amplitude
def calc3Oamp(signal):
    signal = cutandzeropad(signal)
    N = signal["dlen"]
    signal["fft"] = 2.0 / N * np.abs(np.fft.rfft(signal["values"])[:int(N/2)])
    signal["fxscale"] = np.linspace(0, signal["srate"]/(2), int(N/2))
    signal["dOamp"] = signal["fft"][int(round(3*f*(N/signal["srate"])))]
    return signal


if __name__ == "__main__":
    sweepam = 1000
    Freq = np.logspace(0,5,5)
    Freq = Freq[::-1]
    amplist = []
    realamplist = []
    for sweep in range(sweepam):
        amps = []
        realamps = []
        for f in Freq:
            signal, virtual3O = signalGen.gen3Osig(f)
            signal = calc3Oamp(signal)
            amps = np.append(amps, signal["dOamp"])
            realamps = np.append(realamps, virtual3O)
        realamplist.append(realamps)
        amplist.append(amps)
    errorlist = []
    for sweep in amplist:
        plt.plot(np.linspace(0.0,5,5), sweep)
    plt.show()
