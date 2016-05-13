#!/usr/bin/env python
# -*- coding:utf-8 -*-

# FIXME: Aktuell ist es noch Python 2, muss ich noch ggf portiert
#        werden. Jedoch scheint es kein python3-mpltoolkits.basemap für
#        Debian Jessie geben.

# FIXME: Das Skript in ein Jupyter Notebook übersetzen.
#        Die wichtigen Kommentare werden in Text-Zellen übersetzt.
#        Die Kommentare mit Hintergrundinformationen würde ich im
#        Quellcode belassen.

# Die ersten beiden Zeilen des Skriptes ist im speziellen für Linux /
# MacOS Systeme gedacht, um zu signalisieren, dass es sich um ein
# Python-Skript handelt. In Windows wird dies an der Dateiendung (*.py)
# erkannt.
# Die zweite Zeile legt den Zeichensatz fest. Dies ist notwendig, damit
# wir Umlaute verwenden können, ohne dass sich der Interpreter
# verschluckt.

# Ebenso wird alles was hinter einem #-Zeichen steht ignoriert.
# Diese wird "Kommentar" genannt.

# FIXME: Ist diese Einleitung notwendig? Oder ist das zuviel?

# Zielsetzung
# ===========

# Am Beispiel dieses Skripts wollen wir folgendes Lernen:
#
# - Wie kann ich Informationen aus einer Datei auslesen?
# - Wie kann ich die gelesenen Informationen weiterverarbeiten?
# - Wie kann ich die Informationen anzeigen?
#
# Das ganze machen wir am Beispiel verschiedener Daten, welche von
# der Stadt Hamburg im [Transparenzportal](transparenz.hamburg.de)
# frei zu Verfügung gestellt werden.
# Die von uns ausgewählten Daten haben gemeinsam, dass sie Ortsbezogen
# sind. Wir wollen diese Daten auf einer Karte darstellen.
# Dabei fixieren wir uns auf die einzelnen Stadtteile der Hansestadt.
# Die Umrisse der einzelnen Stadtteil wurden aus
# [Open Street Map](www.openstreetmap.org), einem offenen, von vielen
# Freiwilligen gepflegten Kartendienst, exportiert.

# Das Skript
# ==========

# Die Mächtigkeit von Python liegt in der Philosopie
# "Batteries included" (Batterien beiliegend) begründet.
# Für jede Aufgabe gibt es bereits ein passendes Werkzeug, dass man
# nur noch einsetzen muss.

# Diese Werkzeuge werden 'Module' genannt und können in unser Skript
# importiert werden. Der Import kann an beliebiger Stelle erfolgen,
# es gehört allerdings zum guten Stil dies am Anfang der Datei zu
# machen.

# Zur Darstellung von Graphen gibt es das Module "Matplotlib". Dieses
# importieren wir und benennen es um, damit wir nicht jedes mal den
# gesamten Namen ausschreiben müssen.
import matplotlib.pyplot as plt

# Zustätzlich werden verschiedene untergeordnete Module importiert,
# um die vielfätigen Möglichkeiten von Matplotlib nutzen zu können.
import matplotlib.colors
import matplotlib.patches
import matplotlib.collections

# Zur Darstellung der Karte nutzen wir das "Basemap"-Modul.
from mpl_toolkits.basemap import Basemap

# "numpy" gehört zu den mächtigeren Modulen von Python. Es stellt eine
# Vielzahl von Hilfsmitteln zur effizienten Verarbeitung von Vektoren.
import numpy as np

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
# FIXME: ggf. Exkurs Koordinatensysteme
import utm
# Zum Zusammenfassen von größeren Datenmengen verwenden wir das
# "collections" (Sammlungen) Modul.
import collections

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

def isStadtteil(f):
    return f['properties'].get('name:prefix') == "Stadtteil"

regions = filter(isStadtteil, raw['features'])

# FIXME: Ich finde die Funktion "filter" sehr elegant. Alternativ könnte
#        man dies aber auch mit einer einfachen Schleife machen.
#        Das ist vermutlich verständlicher
#
# regions = []
# for feature in raw['features']:
#     if feature['properties'].get('name:prefix') == "Stadtteil":
#         regions.append(feature)

# Im nächsten Schritt ordnen wir jedem Stadtteil (definiert nur den
# Namen), den entsprechenden Umriss zu.
# Dabei ignorieren wir Stadtteile die keinen Namen haben.
# Ebenso werden Stadtteile ignoriert die keine Umrisse haben.

borders = {
    region['properties'].get('name'):
        (region['geometry']['coordinates'][0], )
        if region['geometry']['type'] == 'Polygon'
    else tuple(map(lambda p: p[0], region['geometry']['coordinates']))
    for region in regions if all([
        region['properties'].get('name'),
        region['geometry']['type'] in ['Polygon', 'MultiPolygon'],
    ])
}

# FIXME: Auch an dieser Stelle ist eine Schleife vermutlich
#        verständlicher als eine dict-comprehension
# borders = {}
# for region in regions:
#     if region['properties'].get('name') is not None and region['geometry']['type'] in ['Polygon', 'MultiPolygon']:
#         if region['geometry']['type'] == 'Polygon':
#             borders[region['properties'].get('name')] = (region['geometry']['coordinates'][0], )
#         else:
#             borders[region['properties'].get('name')] = tuple(map(lambda p: p[0], region['geometry']['coordinates']))


# Exemplarisch wolllen wir jetzt die Schule Anzahl der Schulen pro
# Stadtteil zählen.
# Hierfür laden wir den Datensatz über die Schulen in Hamburg.
raw_data = geojson.load(open("data/schulen.geojson"))

# Zu dem Datensatz gehört auch die Anzahl der Schüler. Leider ist diese
# Information unvollständig, sodass wir unter Umständen eine Anzahl '0'
# annehmen müssen.


def NoneIsZero(value):
    return 0 if value is None else value

schools = [
    {
        'name': feature['properties'].get('Name'),
        'region': feature['properties'].get('stadtteil'),
        'position': utm.to_latlon(feature['geometry']['coordinates'][0],
                                  feature['geometry']['coordinates'][1],
                                  32, 'N'),
        'value': NoneIsZero(feature['properties'].get('schueleranzahl')),
    } for feature in raw_data['features']
]

# FIXME: List-Comprehension als Schleife
#
# schools = []
# for feature in raw_data['features']:
#     schools.append({
#        'name': feature['properties'].get('Name'),
#        'region': feature['properties'].get('stadtteil'),
#        'position': utm.to_latlon(feature['geometry']['coordinates'][0],
#                                  feature['geometry']['coordinates'][1],
#                                  32, 'N'),
#        'value': NoneIsZero(feature['properties'].get('schueleranzahl')),
#     })

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

# Ein Diagramm ist schonmal nicht schlecht, aber eine Karte ist hübscher!
# Wir wählen einen Kartenauschnitt, der ganz Hamburg umfasst.
corners = (
    (53.75, 10.33),  # Obere rechte Ecke
    (53.39, 9.72),  # Untere linke Ecke
)

# Für die Karte nutzen wir das zuvor geladene "Basemap"-Modul
# Die Karte bindet sich selbstständig an Matplotlib an.
city_map = Basemap(projection='merc',  # Merkator-Projektion ist Standard für Karten
                   # Obere rechte Ecke des Sichtbereiches
                   urcrnrlat=corners[0][0], urcrnrlon=corners[0][1],
                   # Untere linke Ecke des Sichtbereiches
                   llcrnrlat=corners[1][0], llcrnrlon=corners[1][1],
                   # Zentrum der Karte
                   lat_0=53.5449, lon_0=9.9731,
                   resolution='h')
city_map.set_axes_limits()

# Um die Anzahlen unterscheiden zu können weisen jeder Anzahl
# eine Farbe zu.
# Der Einfachheit halber verwenden wir eine vorgefertige.
colors = matplotlib.cm.get_cmap('Spectral')
# Matplotlib kann nur Zahlen zwischen 0.0 und 1.0 darstellen.
# Daher erzeugen wir uns eine Möglichkeit unsere Zahlen zu
# "normalisieren".
# FIXME: Dies kann man gut an einem Beispiel erklären.
normalize = matplotlib.colors.Normalize(vmin=min(count.values()),
                                        vmax=max(count.values()))

# Aktuell sind die Grenzen der Stadtteile durch Paare aus Längen- und
# Breitengrad definiert. Matplotlib benötigt jedoch zwei getrennte
# Listen mit jeweils eine mit allen Längengraden und eine mit allen
# Breitengraden.
# Wir transformieren unsere Stadtteilgrenzen entsprechend.
outlines = {
    name: tuple(
        (
            [lon for lon, lat in polygon],
            [lat for lon, lat in polygon]
        ) for polygon in polygons
    ) for name, polygons in borders.iteritems()
}

# FIXME: dict-comprehension als Schleife
#
# outlines = {}
# for name, polygons in borders.items():
#     outlines[name] = []
#     for polygon in polygons:
#         outlines[name].append((
#             [lon for lon, lat in polygon],
#             [lat for lon, lat in polygon]
#         ))

# Im nächsten Schritt können wir jetzt alle Sammlung aller Grenzpolygone
# erzeugen um diese auf der Karte zu zeichnen.
# Wir erzeugen zuerst eine Sammlung, da wir dann in einem einzigen
# Schritt zeichen können. (Zeichnen dauert lange.)
# Gleichzeitig wollen wir eine Liste der Schulanzahlen erstellen,
# damit wir eine Legende neben der Karte anzeigen können.
patches = []
counts = []
for name, polygons in outlines.items():
    for (lons, lats) in polygons:
        # Die Koordinaten liegen sind nach wie vor in Längen- und
        # Breitengraden angegeben.
        # Um die Karte darstellen zu können, müssen wir diese in
        # einzelne Pixelposition umwandeln. Diese macht die Karte für
        # uns.
        x, y = city_map(lons, lats)
        # Anschließend fügen wir die Koordinaten zum einem Objekt
        # zusammen und erzeugen das Polygon.
        xy = zip(x, y)
        patches.append(matplotlib.patches.Polygon(xy))
        # Aus der zuvor generierten Zählung der Stadtteile nehmen wir
        # die Anzahl der Schulen in unsere Zählungsliste auf.
        counts.append(count[name])

# Nachdem wir alle Polygon erstellt haben fügen wird diese mit den
# Farb- und Normalisierungsinformationen zusammen.
p = matplotlib.collections.PatchCollection(patches,
                                           cmap=colors,
                                           norm=normalize,
                                           alpha=0.7)
# Jeden Polygon in der Sammlung wird jetzt die Anzahl der Schulen
# zugewiesen. Dies erscheint ein wenig nach doppelter Arbeit, leider
# scheint es keinen direkteren Weg zu geben.
p.set_array(np.array(counts))
# Die Polygone der Stadtteilgrenzen werden in den Plot eingefügt.
plt.gca().add_collection(p)
# Dem Plot wird eine Legende hinzugefügt, damit die Farben eine
# sichtbare Bedeutung erhalten.
plt.colorbar(p,
             spacing="proportional",
             ticks=range(max(counts) + 1),
             boundaries=range(max(counts) + 1))

# Bonus: Wir wollen die Position jeder Schule durch einen Punkt auf der
# Karte markieren.
# Hierfür erzeugen wir eine Liste alle Positionen der einzelnen Schulen.
positions = zip(*[school['position'] for school in schools])
# Wir definieren die Größe der Punkte auf 10 Pixel.
size = 10
# FIXME: Aufgabe: Passe die Größe der Kreise an die Anzahl der Schüler
#                 an.
# FIXME: Lösung:  size = [float(school['value']) / 10 for school in schools]

# Wie schon zuvor bei den Stadtteilgrenzen müssen wir auch die
# Koordinaten der Schulen von Längen- und Breitengraden in
# Pixelpositionen umrechneen (lassen).
x, y = city_map(positions[1], positions[0])
# Die Darstellung durch Punkte nennt man "Scatter-Plot".
# Das "k" gibt an, dass die Punkt die Farbe schwarz haben sollen.
plt.scatter(x, y, size, "k")

# Jede Darstellung sollte einen Titel bekommmen.
plt.title("Anzahl der Schulen")

# Wir sind fertig und können die Karte anzeigen.
plt.show()


# TODO:
#       - Eine Möglichkeit schaffen Elemente zu zählen die nur eine
#         Position haben, aber keinem Stadtteil zugeordnet sind.
#         Dies kann durch Prüfung ob ein Punkt innerhalb eines Polygons
#         ist erfolgen.
#       - Eine Möglichkeit schaffen Elemente anzugeigen, die nicht nur
#         ein Punkt sind:
#           - Linien (zum Beispiel Radwege)
#           - Flächen (zum Beispiel Parkanlagen)
