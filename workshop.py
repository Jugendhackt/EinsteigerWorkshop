#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Hey, ich bin ein Python-Skript.
# Alles was hinter einem #-Zeichen steht wird ignoriert.
# Dies wird "Kommentar" genannt.

# Am Beispiel dieses Skripts wollen wir folgendes Lernen:
#
# - Wie kann ich Informationen aus einer Datei auslesen?
# - Wie kann ich die gelesenen Informationen weiterverarbeiten?
# - Wie kann ich die Informationen anzeigen?

# Das ganze machen wir am Beispiel verschiedener Daten, welche von
# der Stadt Hamburg im [Transparenzportal](transparenz.hamburg.de)
# frei zu Verfügung gestellt werden.
# Die von uns ausgewählten Daten haben gemeinsam, dass sie Ortsbezogen
# sind. Wir wollen diese Daten auf einer Karte darstellen.
# Dabei fixieren wir uns auf die einzelnen Stadtteile der Hansestadt.
# Die Umrisse der einzelnen Stadtteil wurden aus
# [Open Street Map](www.openstreetmap.org), einem offenen, von vielen
# Freiwilligen gepflegten Kartendienst, exportiert.

# Die Mächtigkeit von Python liegt in der Philosopie
# "Batteries included" (Batterien beiliegend) begründet.
# Für jede Aufgabe gibt es bereits ein passendes Werkzeug, dass man
# nur noch einsetzen muss.

# Diese Werkzeuge werden 'Module' genannt und können in unser Skript
# importiert werden. Der Import kann an beliebiger Stelle erfolgen,
# es gehört allerdings zum guten Stil dies am Anfang der Datei zu
# machen.

# Die Daten die wir verarbeiten wollen liegen im Format "GeoJSON" vor.
# Auch hierfür gibt es eine Modul, welches uns die Daten laden lässt.
import geojson
# Koordinaten auf der Karte werden in Längen- und Breitengraden
# angegeben. Ein Teil der Koordinaten liegt jedoch nur in
# "Universal Transverse Mercator" Darstellung vor. Glücklicherweise
# existiert hierfür ein Modul, mit dem wir diese in die von uns
# benötigen Längen- und Breitengrade konvertieren können.
# Wir müssen daher nicht verstehen wie dieses System im speziellen
# aufgebaut ist.
import utm
# Zum Zusammenfassen von größeren Datenmengen verwenden wir das
# "collections" (Sammlungen) Modul.
import collections

# Für den Workshop haben wir ein gesondertes Modul entwickelt, dass
# Hamburg für uns zeichnen kann.
import hamburg

# Nachdem wir alle benötigten Module geladen haben, können wir mit dem
# eigentlichen Skript beginnen.

# Zuerst laden wir die Karteninformationen.
raw = geojson.load(open("data/hamburg.geojson"))
# FIXME: An dieser Stelle wäre ggf ein Exkurs JSON / GeoJSON angebracht.
#        Dieser könnte genutzt werden um grundlegende Datenstrukturen
#        (Listen / Dictionaries) zu erklären.


# Aus den vorliegenden Rohdaten wolen wir die Grenzen der Stadtteile
# extrahieren.
# Hierfür müssen wir nur die 'features' berücksichtigen, welche als
# "Stadtteil" markiert sind.

regions = []
for feature in raw['features']:
    if feature['properties'].get('name:prefix') == "Stadtteil":
        regions.append(feature)

# Im nächsten Schritt ordnen wir jedem Stadtteil (definiert nur den
# Namen), den entsprechenden Umriss zu.
# Dabei ignorieren wir Stadtteile die keinen Namen haben.
# Ebenso werden Stadtteile ignoriert die keine Umrisse haben.

borders = {}
for region in regions:
    if region['properties'].get('name') is not None and region['geometry']['type'] in ['Polygon', 'MultiPolygon']:
        if region['geometry']['type'] == 'Polygon':
            borders[region['properties'].get('name')] = (region['geometry']['coordinates'][0], )
        else:
            borders[region['properties'].get('name')] = tuple(map(lambda p: p[0], region['geometry']['coordinates']))


# Exemplarisch wolllen wir jetzt die Schule Anzahl der Schulen pro
# Stadtteil zählen.
# Hierfür laden wir den Datensatz über die Schulen in Hamburg.
raw_data = geojson.load(open("data/schulen.geojson"))

# Zu dem Datensatz gehört auch die Anzahl der Schüler. Leider ist diese
# Information unvollständig, sodass wir unter Umständen eine Anzahl '0'
# annehmen müssen.


def NoneIsZero(value):
    return 0 if value is None else value

schools = []
for feature in raw_data['features']:
    schools.append({
        'name': feature['properties'].get('Name'),
        'region': feature['properties'].get('stadtteil'),
        'position': utm.to_latlon(feature['geometry']['coordinates'][0],
                                  feature['geometry']['coordinates'][1],
                                  32, 'N'),
        'value': NoneIsZero(feature['properties'].get('schueleranzahl')),
    })

# Jetzt zählen wir die Anzahl Schulen in jedem Stadtteil

count = collections.defaultdict(int)
for school in schools:
    count[school['region']] += 1

# FIXME: An dieser Stelle könnte man eine erste Visualisierung vornehmen
#        und sich den Inhalt der Variable `count` anschauen.
#        Ich halte das für ein ersten Erfolgerlebnis ganz wichtig.

# FIXME: Als nächsten kann eine Visualsierung als Diagramm vorgenommen
#        werden um die Wirksamkeit von Visualierung zu demonstrieren.
#        Ich denke dies ist auch als weiteres Erfolgerlebnis sinnvoll.
#
# plt.bar(range(len(count)), count.values(), align='center')
# plt.xticks(range(len(count)), count.keys(), rotation=45)
# plt.show()

# Zuerst zeichnen wir die Positionen der Schulen
hamburg.draw_positions(schools)

# Dann zeichnen wir die einzelnen Stadtteile
hamburg.draw_regions(borders, count)

# Jede Darstellung sollte einen Titel bekommmen.
hamburg.set_title("Anzahl der Schulen")

# Wir sind fertig und können die Karte anzeigen.
hamburg.show()
