#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________


from threading import RLock

from pyshock.core.action import Action
from pyshock.device.device import Device

lock = RLock()

class Pacdog(Device):

    button_codes = [
        #8 22 23
        [0, 0, 0],  # E/P left
        [0, 1, 1],  # B1  right 1
        [0, 1, 0],  # B2  right 2, E/P right
        [1, 1, 0],  # B3  right 3
        [1, 0, 0],  # B4  left 1
        [0, 0, 1],  # B5  left 2
        [1, 0, 1],  # B6  left 3
        [1, 1, 1]   # unused
    ]

    def __init__(self, name, color, code, button):
        super().__init__(name, color)
        self.code = code
        self.button = button

    def is_sdr_required(self):
        return True

    def boot(self, _arduino_manader, sdr_sender):
        self.sender = sdr_sender

    def generate(self, code, intensity, button, beep):
        pre_checksum = code[0:2] + self.calculate_intensity_code(intensity) + str(self.button_codes[button][0]) + code[2:]
        post_checksum = str(beep) + str(self.button_codes[button][1]) + str(self.button_codes[button][2])
        data = pre_checksum + "CCCCC" + post_checksum
        return pre_checksum + self.calculate_checksum(data) + post_checksum

    def calculate_intensity_code(self, intensity):
        res = ""
        for i in range(0, 6):
            res = res + str(intensity // 2**i % 2)
        return res

    def calculate_checksum(self, data):
        # a b c d e f g h i  j  k  l  m  n  o  p q   r  s
        # 7 6 5 4 3 2 1 0 15 14 13 12 11 10 09 8 23 22 21
        res =       str((int(data[0]) + int(data[ 8])) % 2)
        res = res + str((int(data[1]) + int(data[ 9]) + int(data[21])) % 2)
        res = res + str((int(data[2]) + int(data[10]) + int(data[22])) % 2)
        res = res + str((int(data[3]) + int(data[11]) + int(data[23])) % 2)
        res = res + str((int(data[4]) + int(data[12])) % 2)
        return res

    def encode(self, data):
        prefix = "0101010101010101111"
        filler = "10"
        res = prefix + filler
        for bit in data:
            res = res + bit + filler
        return res


    def send(self, data):
        self.sender.send(
            frequency=27.1e6,
            sample_rate=2e6,
            carrier_frequency=27.1e6,
            modulation_type="FSK",
            samples_per_symbol=3100,
            low_frequency=92e3,
            high_frequency=95e3,
            pause=262924,   # TODO: Why was this 2*?
            data=data)


    def command(self, action, level, duration):
        message = ""
        if action == Action.BEEPZAP:
            message = self.encode(self.generate(self.code, 0, self.button, 1)) + "/1s"

        beep = 1
        if action == Action.ZAP or action == Action.BEEPZAP:
            beep = 0

        if (duration < 250):
            duration = 250

        message_template = self.encode(self.generate(self.code, level * 63 // 100, self.button, beep))
        for _ in range(0, (duration + 5) // 250):
            message = message + " " + message_template

        self.send(message)


    def assertThat(self, message, expected, actual):
        if expected == actual:
            print(message + ": pass")
        else:
            print(message + ": FAILED")
            print("   Expected: " + expected)
            print("   Actual  : " + actual)

    def test_encoding(self):
        expected = "010101010101010111110010110010110010010110010010010110110010110110010010010010010010110110010"
        data = "010100100011011000000110"
        encoded = self.encode(data)
        self.assertThat("encoding", expected, encoded)

    def test_generate(self):
        expected = "010100100011011000000110"
        generated = self.generate("010110110", 18, 2, 1)
        self.assertThat("generation", expected, generated)

    def test_calculate_intensity_code(self):
        self.assertThat("intensity  1", "100000", self.calculate_intensity_code(1))
        self.assertThat("intensity 32", "000001", self.calculate_intensity_code(32))

    def test(self):
        self.test_encoding()
        self.test_generate()
        self.test_calculate_intensity_code()

"""
message = encode(generate("011100000", 20, 0, 1)) + "/1s"
for i in range(0, 4):
    message = message + " " + encode(generate("011100000", 20, 0, 0))

send(message)
"""

#test()
