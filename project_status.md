# Projektstatus – SwitchBot Relay 2PM Cover

**Stand:** 24.10.2026  
**Repository:** https://github.com/The-Fox23/switchbot-relay-2pm-cover  
**Status:** Mehrgeräte-Erkennung und Messwertsensoren im Code ergänzt; Tests in Home Assistant stehen aus.

## 1. Projektziel

Eine eigene Home-Assistant-Integration für den **SwitchBot Relay Switch 2PM**, die Geräte als native Cover-Entitäten für Rollläden bereitstellt und elektrische Messwerte über die SwitchBot Cloud API ausliest.

## 2. Automatische Geräteerkennung

- Beim Einrichten werden alle unterstützten Relay Switch 2PM im SwitchBot-Konto gesucht.
- Jedes gefundene Gerät erhält eine eigene Cover-Entität und Messwertsensoren.
- Geräteliste und Statusdaten werden alle 30 Sekunden aktualisiert.
- Neu hinzugefügte Geräte sollen nach einer erfolgreichen Aktualisierung automatisch als Entitäten erscheinen.
- Ein Statusfehler eines einzelnen Geräts soll die übrigen Geräte nicht blockieren.

**Hinweis zu bestehenden Installationen:** Alte Konfigurationseinträge mit gespeicherter Geräte-ID werden weiterhin mit den vorhandenen Zugangsdaten geladen. Wenn mehrere alte Einträge für dasselbe Konto existieren, können mehrere Coordinator dieselben API-Abfragen ausführen. Eine automatische Zusammenführung alter Einträge wurde nicht implementiert.

## 3. Elektrische Messwertsensoren – neu

Für jeden Relay Switch 2PM werden pro Kanal (Switch 1 und Switch 2) drei Sensoren angelegt:

| Messwert | API-Feld | Home Assistant Einheit |
|---|---|---|
| Spannung | `switch1Voltage` / `switch2Voltage` | V |
| Leistung | `switch1Power` / `switch2Power` | W |
| Stromstärke | `switch1ElectricCurrent` / `switch2ElectricCurrent` | A |

Die API liefert die Stromstärke in Milliampere; die Integration rechnet sie für die Home-Assistant-Einheit Ampere um. Wenn ein Feld in der API-Antwort fehlt, bleibt der jeweilige Sensorwert leer (`None`) statt einen Messwert zu erfinden.

Die Messwerte werden gemeinsam mit dem Geräte-Status im bestehenden 30-Sekunden-Intervall abgefragt. Es wird kein zusätzlicher API-Aufruf je Sensor ausgelöst.

**Noch nicht praktisch verifiziert:** Ob die API für das konkrete Gerät und die installierte Firmware alle sechs Felder tatsächlich mit Werten liefert. Fehlende Felder können zu leeren Sensorwerten führen.

## 4. Bisherige Erkenntnisse und Tests

Vom Nutzer bestätigt:
- Öffnen und Schließen funktionieren.
- Die Positionsrückmeldung funktioniert.
- Gemeldete API-Positionen 0, 28, 54 und 100 passten zu den beobachteten Rollladenpositionen.

Weitere zuvor beobachtete Werte: `online: true`, `calibrate: true`, `isStuck: false`.

Die native API-Stoppfunktion `pause` ist implementiert, aber noch nicht praktisch bestätigt.

## 5. Positionsumrechnung

- SwitchBot: `0 = offen`, `100 = geschlossen`
- Home Assistant Cover: `100 = offen`, `0 = geschlossen`

```text
home_assistant_position = 100 - switchbot_position
switchbot_target_position = 100 - home_assistant_target_position
```

## 6. Geänderte Dateien

- `sensor.py` – sechs Messwertsensoren pro Gerät (Spannung, Leistung und Stromstärke auf beiden Kanälen).
- `const.py` – aktiviert Cover- und Sensor-Plattform.
- `README.md` – dokumentiert Messwerte und Einheiten.
- `project_status.md` – Status und ausstehende Tests aktualisiert.

## 7. Offene Aufgaben

- [ ] Python-Syntax und Imports prüfen.
- [ ] Gegen die installierte Home-Assistant-Core-Version prüfen.
- [ ] Prüfen, ob beide Kanäle Spannung, Stromstärke und Leistung liefern.
- [ ] Werte mit einer unabhängigen Anzeige/Messung vergleichen.
- [ ] Mehrgeräte-Erkennung und dynamisches Hinzufügen testen.
- [ ] Offline-Verhalten und API-Ausfälle testen.
- [ ] Native `pause`-Stoppfunktion testen.
- [ ] HACS-Validierung prüfen.

## 8. Sicherheit und Veröffentlichung

- API-Token und API-Secret niemals in Git-Dateien, Screenshots, Logs oder öffentlichen Issues veröffentlichen.
- Die Steuerung läuft über die SwitchBot Cloud API und hängt von Internet- und Cloud-Verfügbarkeit ab.
- Die Integration ist kein Sicherheits- oder Schutzsystem.
- Versionsnummer, Release-Tag und Veröffentlichung pflegt der Nutzer manuell.

**Nächster Schritt:** Code installieren und prüfen, ob unter jedem Relay-Gerät sechs Sensoren erscheinen und sinnvolle Werte aktualisiert werden.
