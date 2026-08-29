SuSt Universe for Mods
----------------------

Dieses kleine Tool stellt in den Programmverzeichnissen von SuSt2 und SSRW aus der SuSt Universe Compilation die in den früheren Versionen der beiden Spiele übliche Ordnerstruktur wieder her. 

Nach dem Starten von SuSt_Universe_for_Mods.exe findet man im Menü "Restructure" die beiden Menüpunkte "SuSt II" und "SSRW". Durch Auswahl dieser Menüpunkte startet man die automatische Umstrukturierung des Programmverzeichnisses von Sudden Strike II bzw. Sudden Strike Resource War. 
Zu Beginn der Umstrukturierung muss in einem Dialog das entsprechende Programmverzeichnis angegeben werden. Danach läuft die Umstrukturierung automatisch ab. Zum Abschluss kann man noch entscheiden, ob man für das Spiel, den Map Editor und den Briefing Editor (letzteres nur bei SuSt II) ein Desktop Icon erzeugen möchte.
Nach der Umstrukturierung kann man die Spiele sowohl über die automatisch erzeugten Icons als auch über die Batch-Dateien (Sudden Strike 2.bat im Ordner game bzw. runr.bat im Ordner Run) starten. Bei SuSt II sorgt eine Korrektur der edit3.ini für (hoffentlich) einwandfreien Start des Editors (bei SSRW nicht erforderlich).

Die bei der Installation angelegten Icons für die Spiele funktionieren auch nach der Umstrukturierung, obwohl beim ersten Start danach eine Fehlermeldung erscheint. Windows passt aber automatisch Ziel und Arbeitsverzeichnis so an, dass anschließend wieder alles klappt. Allerdings geht dabei das Bild des Icons verloren. 
Auch wenn es einfacher ist, dieses Icon zu löschen und mit dem von SuSt Universe for Mods automatisch erzeugten Icon zu arbeiten, mit der folgenden Anleitung kann man auch das ursprüngliche Icon wieder herstellen:
- Rechtsklick auf das Icon, im Kontextmenü "Eigenschaften" wählen
- Im Eigenschaftendialog auf "Anderes Symbol" klicken
- Die erscheinende Meldung mit OK bestätigen
- Im Fenster "Anderes Symbol" auf "Durchsuchen..." klicken
- Im Dateidialog die game_exe.exe (im Programmverzeichnis von SuSt II im Ordner
  game\code\Release, bei SSRW im Ordner Run\code\Release) suchen, dann erscheint ein   Fenster, in dem das gewohnte Symbol zu sehen ist.
- Zwei Klicks auf "OK", fertig.
Diese Methode funktioniert sowohl für das Icon auf dem Desktop als auch für das im Startmenü.

Noch eine Anmerkung zur Deinstallation von SuSt II bzw. SSRW:
Bei der SuSt Universe DVD kommt ein anderer Installer/Uninstaller zum Einsatz als bei früheren Versionen. Mit der uninstall.exe im jeweiligen Programmverzeichnis klappt die Deinstallation auch nach der Umstrukturierung noch. Aus diesem Grund ist der Uninstall-Ordner entfallen.
 
Sollte eine Fehlermeldung über eine nicht gefundene Batch-Datei erscheinen, liegt das wahrscheinlich an der Ausführung des Programms ohne Administrator-Rechte. Das Programm darf dann keine Änderungen innerhalb von C:\Programme vornehmen. Wenn Ihr die Schreibrechte für die Programmverzeichnisse von SuSt II und SSRW habt, müsste eigentlich alles klappen.

Dank an Panzergrenadier und Kasper, die mit ihren Anleitungen zum Umbau der Verzeichnisse die Vorarbeit geleistet haben.