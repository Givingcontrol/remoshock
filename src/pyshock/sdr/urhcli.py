#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________

import subprocess
import threading

from pyshock.sdr.sdrsender import SdrSender


lock = threading.RLock()

class UrhCliSender(SdrSender):

    def __init__(self, sdr):
        self.sdr = sdr

    def send(self, frequency, sample_rate, carrier_frequency, 
                 modulation_type, samples_per_symbol, low_frequency,
                 high_frequency, pause, data):

        with lock:
            cmd = [
                "urh_cli",
                "--transmit",
                "--device", self.sdr,
                "--frequency", str(frequency),
                "--sample-rate", str(sample_rate),
                "--carrier-frequency", str(carrier_frequency),
                "--modulation-type", modulation_type,
                "--samples-per-symbol", str(samples_per_symbol),
                "--parameters", str(low_frequency), str(high_frequency),
                "--pause", str(pause),
                "--if-gain", "47",
                "--messages", data]
            print(cmd)
            subprocess.run(cmd)