#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Ein Rätsel
wort = raw_input("Wie lautet das geheime Wort? ")

# Mit == können wir zwei Werte / Variablen vergleichen
if wort == "Alpaka":
    print("Richtig! Die geheime Wort ist {}!".format(wort))
else:
    print("{} ist leider falsch!".format(wort))
