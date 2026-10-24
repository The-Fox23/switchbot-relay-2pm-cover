# Projektstatus – SwitchBot Relay 2PM Cover

**Stand:** 24.10.2026  
**Repository:** https://github.com/The-Fox23/switchbot-relay-2pm-cover  
**Status:** Mehrgeräte-Erkennung und aggregierte Messwertsensoren im Code ergänzt; Tests in Home Assistant stehen aus.

## 1. Projektziel

Eine eigene Home-Assistant-Integration für den SwitchBot Relay Switch 2PM als native Cover-Entität mit Positionssteuerung und elektrischen Messwerten.

## 2. Cover-Symbol

Die Cover-Entität verwendet jetzt das Icon `mdi:window-shutter`, passend zur Rollladen-/Cover-Funktion.

## 3. Messwertsensoren

Pro Gerät gibt es vier Sensoren, ohne getrennte Namen für Switch 1 und Switch 2:

| Sensor | Berechnung | Einheit |
|---|---|---|
| Voltage | Spannung Kanal 1, ersatzweise Kanal 2 | V |
| Current | Summe der Ströme beider Kanäle | A |
| Power | Summe der Leistungen beider Kanäle | W |
| Daily energy | Summe des täglichen Verbrauchs beider Kanäle | kWh |

Die API-Felder für Energie sind `switch1UsedElectricity` und `switch2UsedElectricity`; laut SwitchBot-API werden sie in Watt-Minuten angegeben. Die Umrechnung lautet `kWh = (Watt-Minuten Kanal 1 + Watt-Minuten Kanal 2) / 60000`. Das ist der **Tagesverbrauch**, kein lebenslanger Gesamtzähler. <https://github.com/OpenWonderLabs/SwitchBotAPI/blob/main/devices/plugs-switches/relay-switch-2pm.md>

Die Stromstärke wird aus mA in A umgerechnet. Spannung wird nicht addiert, weil beide Kanäle dieselbe Netzversorgung nutzen; Kanal 1 wird bevorzugt.

## 4. Geräteerkennung und Aktualisierung

- Alle unterstützten Relay Switch 2PM des Kontos werden automatisch gesucht.
- Neue Geräte sollen beim nächsten erfolgreichen Polling automatisch hinzugefügt werden.
- Cover und Messwertsensoren verwenden dieselbe Statusabfrage alle 30 Sekunden.
- Mehrere alte Konfigurationseinträge für dasselbe Konto können weiterhin doppelte API-Abfragen verursachen.

## 5. Bisherige Tests

Vom Nutzer bestätigt:
- Öffnen und Schließen funktionieren.
- Positionsrückmeldung funktioniert.

Noch nicht praktisch bestätigt:
- automatische Erkennung mehrerer Geräte,
- aggregierte Spannung, Stromstärke und Leistung,
- Tagesenergie aus den API-Feldern,
- native `pause`-Stoppfunktion.

## 6. Offene Aufgaben

- [ ] Python-Syntax und Imports prüfen.
- [ ] Gegen die installierte Home-Assistant-Core-Version prüfen.
- [ ] Prüfen, ob die API für beide Kanäle die Messwert- und Energie-Felder liefert.
- [ ] Summen und Energieumrechnung mit SwitchBot-App-Werten vergleichen.
- [ ] Prüfen, wie sich der tägliche Energiezähler beim Tageswechsel verhält.
- [ ] Mehrgeräte-Erkennung und dynamisches Hinzufügen testen.
- [ ] Native `pause`-Stoppfunktion testen.
- [ ] HACS-Validierung prüfen.

## 7. Sicherheit und Veröffentlichung

API-Token und API-Secret nicht in Git-Dateien, Screenshots, Logs oder öffentlichen Issues veröffentlichen. Die Integration hängt von der SwitchBot Cloud API ab und ist kein Sicherheits- oder Schutzsystem. Versionsnummer und Release-Tag pflegt der Nutzer manuell.

**Nächster Schritt:** Nach Installation prüfen, ob pro Gerät genau vier Sensoren erscheinen und ob die Tagesenergie zur SwitchBot-App passt.
