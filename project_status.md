# Projektstatus – SwitchBot Relay 2PM Cover

**Stand:** 24.10.2026  
**Repository:** https://github.com/The-Fox23/switchbot-relay-2pm-cover  
**Status:** Öffnen, Schließen und Positionsrückmeldung praktisch bestätigt; Stopp-Funktion fehlerhaft und in Untersuchung

## 1. Projektziel

Eine eigene Home-Assistant-Integration für den **SwitchBot Relay Switch 2PM**, die das Gerät als native Cover-Entität für einen Rollladen bereitstellt.

Die Integration soll unabhängig von der offiziellen SwitchBot-Integration funktionieren und über die SwitchBot Cloud API kommunizieren.

## 2. Bisherige Erkenntnisse und Tests

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

**Praxistest durch den Nutzer:** Öffnen, Schließen und Übertragung der aktuellen Position funktionieren in der installierten Integration. Die Stopp-Funktion wurde getestet und funktioniert derzeit nicht. Der bisherige `turnOff`-Ansatz ist nicht bestätigt und muss überarbeitet werden.

## 3. Positionsumrechnung

SwitchBot und Home Assistant verwenden entgegengesetzte Prozentwerte:

- SwitchBot: `0 = offen`, `100 = geschlossen`
- Home Assistant Cover: `100 = offen`, `0 = geschlossen`

Daher gilt:

```text
home_assistant_position = 100 - switchbot_position
switchbot_target_position = 100 - home_assistant_target_position
```

Beispiele:
- Home Assistant „Öffnen“ → SwitchBot Zielposition `0`
- Home Assistant „Schließen“ → SwitchBot Zielposition `100`
- Home Assistant Zielposition `50 %` → SwitchBot Zielposition `50`

## 4. Repository und bisher angelegte Dateien

Im Repository wurde auf dem Branch `main` ein erstes Integrationsgerüst angelegt:

- `README.md` – Projektbeschreibung und Installationshinweise
- `hacs.json` – HACS-Metadaten
- `custom_components/switchbot_relay_cover/manifest.json` – Integrationsmanifest
- `custom_components/switchbot_relay_cover/const.py` – Konstanten
- `custom_components/switchbot_relay_cover/api.py` – signierte SwitchBot-API-Anfragen
- `custom_components/switchbot_relay_cover/coordinator.py` – Statusabfrage und Aktualisierung
- `custom_components/switchbot_relay_cover/config_flow.py` – Einrichtung und Geräteauswahl
- `custom_components/switchbot_relay_cover/__init__.py` – Setup und Entladen
- `custom_components/switchbot_relay_cover/cover.py` – Cover-Entität mit Öffnen, Schließen und Positionierung
- `custom_components/switchbot_relay_cover/strings.json` – Konfigurationstexte
- `custom_components/switchbot_relay_cover/translations/en.json` – englische Übersetzungen

Die Geräteauswahl ist aktuell auf den Typ „Relay Switch 2PM“ eingeschränkt.

## 5. Geplante Funktionen

- Einrichtung über **Einstellungen → Geräte & Dienste → Integration hinzufügen**
- Token und Secret als Konfigurationseintrag speichern
- Passendes Relay Switch 2PM aus der SwitchBot-Geräteliste auswählen
- Native Home-Assistant-Cover-Entität bereitstellen — umgesetzt
- Öffnen und Schließen — vom Nutzer erfolgreich getestet
- Zielposition in Prozent einstellen — implementiert; separater Praxistest nicht bestätigt
- Istposition aus dem API-Status auslesen — vom Nutzer erfolgreich getestet
- Status regelmäßig aktualisieren
- HACS-Installation über ein öffentliches GitHub-Repository ermöglichen

## 6. Offene Aufgaben

### Priorität 1 – Code prüfen und korrigieren

- [ ] Alle Python-Dateien auf Syntaxfehler prüfen.
- [ ] Gegen die aktuell unterstützte Home-Assistant-Core-Version prüfen.
- [ ] Config-Flow- und Übersetzungsdateien auf Kompatibilität prüfen.
- [ ] Prüfen, ob SwitchBot den Relay Switch 2PM in der Geräteliste exakt mit dem erwarteten Gerätetyp meldet.
- [ ] API-Antworten und Fehlerfälle robust behandeln.
- [ ] Sicherstellen, dass Positionswerte als Ganzzahlen verarbeitet und ungültige oder fehlende Werte sicher behandelt werden.

### Priorität 2 – In Home Assistant testen

- [ ] Integration lokal installieren und Home Assistant neu starten.
- [ ] Einrichtung mit gültigem API-Token und Secret durchführen.
- [ ] Gerät wird bei der Einrichtung gefunden und ausgewählt.
- [ ] Gemeldete Position stimmt mit der manuellen API-Abfrage überein.
- [x] Öffnen und Schließen testen — laut Nutzer erfolgreich.
- [ ] Zwischenpositionen separat testen und die Rückmeldung nach dem Befehl prüfen.
- [ ] Stopp-Funktion korrigieren und mit dem realen Gerät sicher testen.
- [ ] Verhalten bei Netzwerkunterbrechung, API-Fehlern und offline geschaltetem Gerät prüfen.
- [ ] Sicherstellen, dass nach einem Neustart keine erneute Einrichtung erforderlich ist.

### Priorität 3 – HACS-Veröffentlichung vorbereiten

- [ ] README und Installationsanleitung nach erfolgreichem Praxistest aktualisieren.
- [ ] Versionsnummer und Changelog pflegen.
- [ ] Passendes Git-Tag und Release erstellen.
- [ ] HACS-Validierung und Repository-Anforderungen prüfen.
- [ ] Erst nach erfolgreichem Test für den normalen Betrieb empfehlen.

## 7. Sicherheit

- API-Token und API-Secret dürfen niemals in Git-Dateien, Screenshots, Logs oder öffentlichen Issues veröffentlicht werden.
- Zugangsdaten ausschließlich lokal im Home-Assistant-Konfigurationsdialog eingeben.
- Da Zugangsdaten zuvor im Chat geteilt wurden, sollten sie in der SwitchBot-App erneuert beziehungsweise widerrufen und neu erstellt werden, bevor die Integration produktiv verwendet wird.
- Die Steuerung erfolgt über die SwitchBot Cloud API und ist von Internet- und Cloud-Verfügbarkeit abhängig.
- Die Integration ist kein Sicherheits- oder Schutzsystem. Vor der Nutzung müssen Endlagen, Kalibrierung und das Verhalten des Rollladens vor Ort geprüft werden.

## 8. Aktueller Gesamtstatus

**Grundgerüst:** angelegt  
**Manuelle API-Statusprüfung:** erfolgreich  
**Positionsumrechnung:** anhand der gemessenen Werte festgelegt  
**Integration in Home Assistant getestet:** nein  
**HACS-Veröffentlichung:** noch nicht bereit

**Nächster Schritt:** Zuerst das angelegte Python-Gerüst prüfen und nötige Korrekturen durchführen. Anschließend die Integration in Home Assistant installieren und mit dem Relay Switch 2PM testen.
