#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Dazu erst mal die Datei (File) aufmachen.
# Das "w" steht für schreiben (write).

with open("Obst.txt", "w") as f:
    # Was reinschreiben.
    f.write("Apfel, Birne, Banane.")

# Nochmal aufmachen. "r" steht für lesen (read).
with open("Obst.txt", "r") as f:
    # Den gesamten Inhalt auslesen
    text = f.read()

print(text)
