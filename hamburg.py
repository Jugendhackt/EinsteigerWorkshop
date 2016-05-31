#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Hey, schön das du interesse daran hast, was hinter den Kulissen
# passiert.
#
# Die ersten beiden Zeilen des Skriptes ist im speziellen für Linux /
# MacOS Systeme gedacht, um zu signalisieren, dass es sich um ein
# Python-Skript handelt. In Windows wird dies an der Dateiendung (*.py)
# erkannt.
# Die zweite Zeile legt den Zeichensatz fest. Dies ist notwendig, damit
# wir Umlaute verwenden können, ohne dass sich der Interpreter
# verschluckt.

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
import utm
# Zum Zusammenfassen von größeren Datenmengen verwenden wir das
# "collections" (Sammlungen) Modul.
import collections

# Wir legen die Größe des Plots fest
matplotlib.rcParams['figure.figsize'] = (20.0, 15.0)

# Nachdem wir alle benötigten Module geladen haben, können wir mit dem
# eigentlichen Skript beginnen.

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

pass


def draw_regions(borders, count):
    # Um die Anzahlen unterscheiden zu können weisen jeder Anzahl
    # eine Farbe zu.
    # Der Einfachheit halber verwenden wir eine vorgefertige.
    colors = matplotlib.cm.get_cmap('Spectral')
    # Matplotlib kann nur Zahlen zwischen 0.0 und 1.0 darstellen.
    # Daher erzeugen wir uns eine Möglichkeit unsere Zahlen zu
    # "normalisieren".
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

    # Im nächsten Schritt können wir jetzt alle Sammlung aller Grenzpolygone
    # erzeugen um diese auf der Karte zu zeichnen.
    # Wir erzeugen zuerst eine Sammlung, da wir dann in einem einzigen
    # Schritt zeichen können. (Zeichnen dauert lange.)
    # Gleichzeitig wollen wir eine Liste der Schulanzahlen erstellen,
    # damit wir eine Legende neben der Karte anzeigen können.
    patches = []
    counts = []
    for name, polygons in outlines.items():
        # Aus der zuvor generierten Zählung der Stadtteile nehmen wir
        # die Anzahl der Schulen in unsere Zählungsliste auf.
        counts.append(count[name])
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
    # Setze die karte wieder zurück auf die Stadt, für den Fall dass
    # Punkte außerhalb gezeichnet wurden.
    city_map.set_axes_limits()
    return plt


def draw_positions(objects):
    # Bonus: Wir wollen die Position jeder Schule durch einen Punkt auf der
    # Karte markieren.
    # Hierfür erzeugen wir eine Liste alle Positionen der einzelnen Schulen.
    positions = zip(*[object['position'] for object in objects])
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
    # Setze die karte wieder zurück auf die Stadt, für den Fall dass
    # Punkte außerhalb gezeichnet wurden.
    city_map.set_axes_limits()
    return plt


def set_title(title):
    # Jede Darstellung sollte einen Titel bekommmen.
    plt.title("Anzahl der Schulen")
    return plt


def show():
    # Wir sind fertig und können die Karte anzeigen.
    plt.show()
    return plt


# Zähle Elemente eines Datensatzes anhand ihrer Position
def count_by_position(regions, data, key=None):
    paths = {
        name: matplotlib.path.Path(
            np.array(polygon),
            ([matplotlib.path.Path.MOVETO] +
             [matplotlib.path.Path.LINETO for _ in range(len(polygon) - 2)] +
             [matplotlib.path.Path.CLOSEPOLY]
             )
        )
        for name, polygons in regions.iteritems()
        for polygon in polygons
    }
    count = collections.defaultdict(int)
    for entry in data:
        for name, path in paths.iteritems():
            pos = entry['position'][1], entry['position'][0]
            if path.contains_point(pos):
                count[name] += int(entry.get(key, 1))
    return count


# Zähle Elemente eines Datensatzes anhand ihrer Region
def count_by_region(regions, data, key=None):
    count = collections.defaultdict(int)
    for entry in data:
        count[entry['region']] += int(entry.get(key, 1))
    return count


# Zeichne eine Menge von Polygonen
def draw_polygons(polygons):
    patches = []
    for (lons, lats) in polygons:
        x, y = city_map(lons, lats)
        xy = zip(x, y)
        patches.append(matplotlib.patches.Polygon(xy, color='k'))
    p = matplotlib.collections.PatchCollection(patches, alpha=0.7)
    plt.gca().add_collection(p)


# Zeichne eine Menge von Linien
def draw_lines(lines):
    patches = []
