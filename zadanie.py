#Import wymaganych regul 
import re       #obsluga wyrazen regularnych 
import json     #zapisywania danych w formacie JSON
import sys      #obsluga argumentow wiersza polecen

#W Pythonie w wersji nizszej niz 3.7 slowniki nie zachowuja kolejnosci dodawania elementow
#Aby pole timestamp bylo zawsze pierwsze w wyjsciowym pliku JSON uzyto collections.OrderedDict
from collections import OrderedDict

def parse_gc_log(nazwa_pliku_wejsciowego, nazwa_pliku_wyjsciowego):
    gc_data = []

#odczytanie linii z pliku
    with open(nazwa_pliku_wejsciowego, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
           
            match = re.match(r'^(.*?):.*: \[(.*?)\s*\((.*?)\)', line)
            if match:
                timestamp_z_log = match.group(1).strip()
                GC_name = match.group(2).strip()
                rodzaj_GC = "{} ({})".format(GC_name, match.group(3).strip())
                
                # Ekstrakcja rozmiarow heap przed i po GC:
                rozmiar_heap_przed_gc_MB = re.search(r'Heap before GC invocations=.*?used (\d+\.\d+)M', ' '.join(lines))
                rozmiar_heap_po_gc_MB = re.search(r'Heap after GC invocations=.*?used (\d+\.\d+)M', ' '.join(lines))

                if rozmiar_heap_przed_gc_MB and rozmiar_heap_po_gc_MB:
                    rozmiar_heap_przed_gc_MB = rozmiar_heap_przed_gc_MB.group(1)
                    rozmiar_heap_po_gc_MB = rozmiar_heap_po_gc_MB.group(1)
                
                # Ekstrakcja rozmiarow Eden i Survivors przed i po GC:
                rozmiar_eden_przed_gc_MB = re.search(r'Eden:\s*(\d+\.\d+)M\(\d+\.\d+M\)->\d+\.\d+B\(\d+\.\d+M\)', ' '.join(lines))
                rozmiar_eden_po_gc_MB = re.search(r'Eden:\s*\d+\.\d+M\(\d+\.\d+M\)->(\d+\.\d+)B\(\d+\.\d+M\)', ' '.join(lines))
                rozmiar_surviors_przed_gc_MB = re.search(r'Survivors:\s*(\d+\.\d+)K->\d+\.\d+K', ' '.join(lines))
                rozmiar_surviors_po_gc_MB = re.search(r'Survivors:\s*\d+\.\d+K->(\d+\.\d+)K', ' '.join(lines))

                # Konwertowanie rozmiaru Eden i Survivors z KB na MB
                if rozmiar_eden_przed_gc_MB and rozmiar_eden_po_gc_MB and rozmiar_surviors_przed_gc_MB and rozmiar_surviors_po_gc_MB:
                    rozmiar_eden_przed_gc_MB = float(rozmiar_eden_przed_gc_MB.group(1)) / 1024
                    rozmiar_eden_po_gc_MB = float(rozmiar_eden_po_gc_MB.group(1)) / 1024
                    rozmiar_surviors_przed_gc_MB = float(rozmiar_surviors_przed_gc_MB.group(1)) / 1024
                    rozmiar_surviors_po_gc_MB = float(rozmiar_surviors_po_gc_MB.group(1)) / 1024

                    gc_data.append (OrderedDict([
                        ("timestamp", timestamp_z_log),
                        ("eden_size", rozmiar_eden_przed_gc_MB),
                        ("survivors_size", rozmiar_surviors_przed_gc_MB), 
                        ("heap_size", rozmiar_heap_przed_gc_MB), 
                        ("GC_name", rodzaj_GC), 
                        ("phase", "before") #wartosc stala
                        ]))

                    gc_data.append (OrderedDict([
                        ("timestamp", timestamp_z_log), 
                        ("eden_size", rozmiar_eden_po_gc_MB),
                        ("survivors_size", rozmiar_surviors_po_gc_MB), 
                        ("heap_size", rozmiar_heap_po_gc_MB), 
                        ("GC_name", rodzaj_GC), 
                        ("phase", "after") #wartosc stala
                        ]))

    #Zapisywanie danych do plku w formacie json
    with open(nazwa_pliku_wyjsciowego, 'w') as outfile:
        for entry in gc_data:
            json.dump(entry, outfile)
            outfile.write('\n')

#Skrypt przyjmuje dwa parametry: nazwe pliku wejsciowego (gc.log) i nazwe pliku wyjsciowego (JSON)
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Parametry uruchomieniowe: python nazwa_skryptu.py <nazwa_pliku_wejsciowego> <nazwa_pliku_wyjsciowego>")
    else:
        nazwa_pliku_wejsciowego = sys.argv[1]
        nazwa_pliku_wyjsciowego = sys.argv[2]
        parse_gc_log(nazwa_pliku_wejsciowego, nazwa_pliku_wyjsciowego)