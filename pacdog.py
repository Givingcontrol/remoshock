#!/usr/bin/python3

import subprocess

button_codes = [
    #9 23 24
    [0, 0, 0],  # E/P left
    [0, 1, 1],  # B1  right 1
    [0, 1, 0],  # B2  right 2, E/P right
    [1, 1, 0],  # B3  right 3
    [1, 0, 0],  # B4  left 1
    [0, 0, 1],  # B5  left 2
    [1, 0, 1],  # B6  left 3
    [1, 1, 1]   # unused
]

def generate(code, intensity, button, beep):
    pre_checksum = code[0:2] + calculate_intensity_code(intensity) + str(button_codes[button][0]) + code[2:]
    post_checksum = str(beep) + str(button_codes[button][1]) + str(button_codes[button][2])
    data = pre_checksum + "CCCCC" + post_checksum
    return pre_checksum + calculate_checksum(data) + post_checksum

def calculate_intensity_code(intensity):
    res = ""
    for i in range(0, 6):
        res = res + str(intensity // 2**i % 2)
    return res

def calculate_checksum(data):
    # a b c d e f g h i  j  k  l  m  n  o  p q   r  s
    # 7 6 5 4 3 2 1 0 15 14 13 12 11 10 09 8 23 22 21
    res =       str((int(data[0]) + int(data[ 8])) % 2)
    res = res + str((int(data[1]) + int(data[ 9]) + int(data[21])) % 2)
    res = res + str((int(data[2]) + int(data[10]) + int(data[22])) % 2)
    res = res + str((int(data[3]) + int(data[11]) + int(data[23])) % 2)
    res = res + str((int(data[4]) + int(data[12])) % 2)
    return res

def encode(data):
    prefix = "0101010101010101111"
    filler = "10"
    res = prefix + filler
    for bit in data:
        res = res + bit + filler
    return res

def send(data):
    cmd = [
        "urh_cli",
        "--transmit",
        "--device", "HackRF",
        "--frequency", "27.1e6",
        "--sample-rate", "2e6",
        "--carrier-frequency", "27.1e6",
        "--modulation-type", "FSK",
        "--samples-per-symbol", "3100",
        "--parameters", "92e3", "95e3",
        "--pause", "262924",
        "--messages", data]
    print(cmd)
    subprocess.run(cmd)

def assertThat(message, expected, actual):
    if expected == actual:
        print(message + ": pass")
    else:
        print(message + ": FAILED")
        print("   Expected: " + expected)
        print("   Actual  : " + actual)

def test_encoding():
    expected = "010101010101010111110010110010110010010110010010010110110010110110010010010010010010110110010"
    data = "010100100011011000000110"
    encoded = encode(data)
    assertThat("encoding", expected, encoded)

def test_generate():
    expected = "010100100011011000000110"
    generated = generate("010110110", 18, 2, 1)
    assertThat("generation", expected, generated)

def test_calculate_intensity_code():
    assertThat("intensity  1", "100000", calculate_intensity_code(1))
    assertThat("intensity 32", "000001", calculate_intensity_code(32))

def test():
    test_encoding()
    test_generate()
    test_calculate_intensity_code()

"""
message = encode(generate("011100000", 20, 0, 1)) + "/1s"
for i in range(0, 4):
    message = message + " " + encode(generate("011100000", 20, 0, 0))

send(message)
"""

test()

