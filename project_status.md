# Projektstatus – SwitchBot Relay 2PM Cover

**Stand:** 24.10.2026  
**Repository:** https://github.com/The-Fox23/switchbot-relay-2pm-cover  
**Status:** Automatische Geräteerkennung implementiert; Praxistest der neuen Mehrgeräte-Logik und der nativen `pause`-Stoppfunktion steht aus.

## 1. Projektziel

Eine eigene Home-Assistant-Integration für den **SwitchBot Relay Switch 2PM**, die ein oder mehrere Geräte als native Cover-Entitäten für Rollläden bereitstellt. Die Kommunikation erfolgt über die SwitchBot Cloud API.

## 2. Neue Änderung: automatische Geräteerkennung

Die Integration wurde von einer einzelnen Geräteauswahl auf eine kontobasierte Erkennung umgestellt:

- Beim Einrichten werden alle unterstützten Relay Switch 2PM im SwitchBot-Konto gesucht.
- Für jedes gefundene Gerät wird eine eigene Cover-Entität erstellt.
- Die Geräteliste wird zusammen mit den Statusdaten regelmäßig aktualisiert (alle 30 Sekunden).
- Taucht später ein weiteres unterstütztes Gerät im Konto auf, wird es bei einer erfolgreichen Aktualisierung automatisch als neue Entität hinzugefügt; ein manuelles Neuladen soll dafür nicht nötig sein.
- Die Entity-Unique-ID basiert auf der SwitchBot-Geräte-ID, damit die Entität unabhängig von der Zahl der vorhandenen Konfigurationseinträge eindeutig bleibt.
- Der Geräte-Status wird pro Gerät abgefragt. Ein Statusfehler eines einzelnen Geräts soll die übrigen Geräte nicht blockieren.

**Wichtiger Hinweis zu bestehenden Installationen:** Bisherige Konfigurationseinträge mit gespeicherter Geräte-ID werden weiterhin gelesen. Die neue Laufzeitlogik entdeckt alle unterstützten Geräte mit den darin gespeicherten Zugangsdaten. Wenn mehrere alte Einträge für dasselbe SwitchBot-Konto vorhanden sind, können mehrere Coordinator dieselben API-Abfragen ausführen; Home Assistant sollte doppelte Entitäten anhand der eindeutigen Geräte-ID verhindern. Eine saubere Zusammenführung alter Einträge wurde nicht implementiert. Vor dem produktiven Einsatz mit mehreren alten Einträgen bitte die Geräte- und Entitätsliste kontrollieren.

## 3. Bisherige Erkenntnisse und Tests

Der SwitchBot-API-Status wurde mit dem Gerät „Test“ manuell geprüft. Die gemeldeten Werte entsprachen den tatsächlichen Rollladenpositionen:

| Tatsächlicher Zustand | SwitchBot-API-Position | Home-Assistant-Cover-Position |
|---|---:|---:|
| Vollständig geöffnet | 0 | 100 % |
| Zwischenposition, Test 1 | 28 | 72 % |
| Zwischenposition, Test 2 | 54 | 46 % |
| Vollständig geschlossen | 100 | 0 % |

Weitere beobachtete Statuswerte:
- `online: true`
- `calibrate: true`
- `isStuck: false`
- Bei den protokollierten Messungen waren `switch1Status` und `switch2Status` nicht allein ausreichend, um die Rollladenposition zu bestimmen. Maßgeblich ist das Feld `position`.

**Praxistest durch den Nutzer:** Öffnen, Schließen und Übertragung der aktuellen Position funktionieren. Die Stopp-Funktion wurde getestet und funktioniert mit `turnOff` nicht. Erneutes Senden der zuletzt gemeldeten Position pausierte nur verzögert. Daher sendet die Integration nun den nativen API-Befehl `pause`; dieser Ansatz ist am Gerät noch nicht bestätigt.

## 4. Geänderte Dateien

- `config_flow.py` – kontobasierte Einrichtung; Auswahl eines einzelnen Geräts entfällt.
- `coordinator.py` – regelmäßige Erkennung aller unterstützten Geräte und Statusabfrage je Gerät.
- `cover.py` – dynamisches Hinzufügen neu erkannter Cover-Entitäten; Befehle werden an die jeweilige Geräte-ID gesendet.
- `__init__.py` – kontobasierter Coordinator wird in `entry.runtime_data` abgelegt.
- `const.py` – Home-Assistant-Plattform-Konstante.
- `strings.json` und `translations/en.json` – Einrichtungstexte für mehrere Geräte.
- `README.md` – automatische Geräteerkennung dokumentiert.

## 5. Positionsumrechnung

SwitchBot und Home Assistant verwenden entgegengesetzte Prozentwerte:

- SwitchBot: `0 = offen`, `100 = geschlossen`
- Home Assistant Cover: `100 = offen`, `0 = geschlossen`

Daher gilt:

```text
home_assistant_position = 100 - switchbot_position
switchbot_target_position = 100 - home_assistant_target_position
```

## 6. Offene Aufgaben

### Priorität 1 – Codequalität und Kompatibilität
- [ ] Python-Syntax und Imports in allen geänderten Dateien prüfen.
- [ ] Gegen die installierte Home-Assistant-Core-Version prüfen.
- [ ] Mehrgeräte-Abfrage, Coordinator-Verhalten und dynamisches Hinzufügen in HA testen.
- [ ] Fehlerfall testen, wenn ein einzelnes Gerät offline ist.
- [ ] Verhalten bei leerer Geräteliste und API-Ausfällen kontrollieren.
- [ ] Bestehende Installationen mit einer und mit mehreren alten Konfigurationseinträgen prüfen.

### Priorität 2 – Praxistests
- [x] Öffnen und Schließen – vom Nutzer erfolgreich getestet.
- [x] Positionsrückmeldung – vom Nutzer erfolgreich getestet.
- [ ] Mehr als ein Relay Switch 2PM wird beim Setup als eigene Cover-Entität angezeigt.
- [ ] Ein nach dem Setup hinzugefügtes Gerät erscheint automatisch spätestens nach einer erfolgreichen Aktualisierung.
- [ ] Native Stoppfunktion mit `pause` am Gerät testen.
- [ ] Zwischenpositionen und Rückmeldung nach Befehlen erneut prüfen.
- [ ] Netzwerkunterbrechung und Wiederherstellung testen.

### Priorität 3 – Veröffentlichung
- [ ] README und Changelog nach Praxistests vervollständigen.
- [ ] Versionsnummer, Tag und Release manuell durch den Nutzer pflegen.
- [ ] HACS-Validierung prüfen.

## 7. Sicherheit

- API-Token und API-Secret nicht in Git-Dateien, Screenshots, Logs oder öffentlichen Issues veröffentlichen.
- Da Zugangsdaten zuvor im Chat geteilt wurden, sollten sie erneuert beziehungsweise widerrufen und neu erstellt werden, bevor die Integration produktiv verwendet wird.
- Die Steuerung läuft über die SwitchBot Cloud API und hängt von Internet- und Cloud-Verfügbarkeit ab.
- Die Integration ist kein Sicherheits- oder Schutzsystem. Endlagen, Kalibrierung und Rollladenverhalten müssen vor Ort geprüft werden.

## 8. Aktueller Gesamtstatus

**Einzelgeräte-Steuerung:** Öffnen, Schließen und Positionsrückmeldung durch Nutzer bestätigt  
**Mehrgeräte-Erkennung:** implementiert, noch nicht praktisch getestet  
**Automatische Ergänzung neuer Geräte:** implementiert, noch nicht praktisch getestet  
**Native Pause/Stopp-Funktion:** implementiert, Praxistest offen  
**HACS-Veröffentlichung:** noch nicht als getestete Version freigegeben

**Nächster Schritt:** Änderungen in Home Assistant installieren bzw. Integration neu laden und prüfen, ob alle vorhandenen Relay Switch 2PM als eigene Cover-Entitäten erscheinen. Anschließend ein weiteres Gerät im SwitchBot-Konto hinzufügen und kontrollieren, ob es innerhalb des Aktualisierungsintervalls automatisch auftaucht.
