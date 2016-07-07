#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random

versuche = 10
meine_zahl = random.randint(0, 100)
deine_zahl = 0

print("Ich habe mir eine Zahl zwischen 1 und 100 ausgedacht.")
print("Welche?")

# != bedeutet ungleich
while versuche > 0 and deine_zahl != meine_zahl:
    # Eine Anweisung in Klammern kann über mehrere Zeilen gehen.
    eingabe = raw_input(
        "Du darfst noch {} mal raten: ".format(versuche)
    )
    try:
        # Eine Eingabe ist ein Text, wir versuchen diesen in eine
        # Zahl umzuwandeln. (int)
        # Nur wenn es tatsächlich eine Zahl ist, können wir
        # weitermachen.
        deine_zahl = int(eingabe)
        if (deine_zahl < 0 or deine_zahl > 100):
            print(
                "Du musst eine Zahl zwischen 1 und 100 eingeben."
            )
        elif deine_zahl < meine_zahl:
            # Wenn unser Text Umlaut enhält müssen wir dies durch
            # ein kleines u markieren.
            print(u"Meine Zahl ist größer!")
            versuche = versuche - 1
        elif deine_zahl > meine_zahl:
            print("Meine Zahl ist kleiner!")
            versuche = versuche - 1
        elif deine_zahl == meine_zahl:
            print("Das ist meine Zahl!")
    except:
        print("Du musst schon eine Zahl eingeben.")
