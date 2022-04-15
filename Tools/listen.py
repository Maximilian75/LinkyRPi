#This file is part of LinkyRPi.
#LinkyRPi is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#LinkyRPi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with LinkyRPi. If not, see <https://www.gnu.org/licenses/>.
#(c)Copyright Mikaël Masci 2022


import serial
import time
from datetime import datetime

list_measures = []

#==============================================================================#
# Traitement de la mesure lue                                                  #
#==============================================================================#
def treatmesure(mesureCode,mesureValue) :
    mesure = (mesureCode, mesureValue)
    list_measures.append(mesure)

    #q1.send(mesureCode + ":" + mesureValue)
    print("[>>]" + mesureCode + " : " + mesureValue)

    return list_measures



#Détection du mode TIC en fonction du BAUDRATE détecté
baud_dict = [1200, 9600]
rateFound = False
rateValue = 0
global modeTIC

for baud_rate in baud_dict:
    print(baud_rate)


    with serial.Serial(port='/dev/ttyAMA0', baudrate=baud_rate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                       bytesize=serial.SEVENBITS, timeout=1) as ser:

        print(" Lecture trames")

        # boucle d'attente du début de trame
        line = ser.readline()
        while b'\x02' not in line:  # recherche du caractère de début de trame
            line = ser.readline()

        # lecture de la première ligne de la première trame
        line = ser.readline()
        print(" Debut de trame détecté à " + datetime.now().strftime("%H:%M:%S.%f"))
        while True :
            line_str = line.decode("utf-8")

            rateFound = False
            if baud_rate == 1200 and "ADCO" in line_str :
                print("Trouvé 1200")
                ar = line_str.split(" ")
                rateFound = True
                break
            elif baud_rate == 9600 and "ADSC" in line_str :
                print("Trouvé 9600")
                ar = line_str.split('\t')
                rateFound = True
                break
            else :
                rateFound = False
                break

        if rateFound :
            print("--->" + ar[0] + " = " + ar[1])
