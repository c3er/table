<map version="0.9.0">
<!--To view this file, download free mind mapping software Freeplane from http://freeplane.sourceforge.net -->
<node TEXT="Abschlusspr&#xe4;sentation" ID="ID_135017075" CREATED="1311259981165" MODIFIED="1311260039106">
<hook NAME="MapStyle" max_node_width="600"/>
<node TEXT="Einleitung" POSITION="right" ID="ID_1036102150" CREATED="1311260099599" MODIFIED="1311260104753"/>
<node TEXT="Anlass" POSITION="right" ID="ID_264379887" CREATED="1311260105709" MODIFIED="1311260113149">
<node TEXT="Beschreibung des Auftraggebers" ID="ID_1990101706" CREATED="1311260127722" MODIFIED="1311260375903">
<node TEXT="Auftraggeber macht Sportwetten" ID="ID_930266359" CREATED="1311268980789" MODIFIED="1311268994371"/>
<node TEXT="Bei einigen Webseiten kann man virtuelle Wetten machen" ID="ID_1795923552" CREATED="1311268994893" MODIFIED="1311269034456"/>
<node TEXT="Kunde m&#xf6;chte Daten aus einer bestimmten Webseite auslesen, um evtl. sein eigenes Verhalten daran anzupassen" ID="ID_228210909" CREATED="1311269034918" MODIFIED="1311269147868"/>
</node>
<node TEXT="Zielbeschreibung" ID="ID_173155384" CREATED="1311260673612" MODIFIED="1311260679761">
<node TEXT="Die Webseite Asianbookie" ID="ID_1274163865" CREATED="1311260545719" MODIFIED="1311260566622">
<node TEXT="Enth&#xe4;lt eine Liste mit allen Teilnehmer" ID="ID_1748530732" CREATED="1311269724679" MODIFIED="1311270215630"/>
<node TEXT="Diese Liste soll ausgelesen und gespeichert werden" ID="ID_618038284" CREATED="1311270216673" MODIFIED="1311270232645"/>
</node>
<node TEXT="Vorf&#xfc;hrung der Webseite" ID="ID_1986427369" CREATED="1311263616896" MODIFIED="1311263627897"/>
</node>
</node>
<node TEXT="Anforderungen" POSITION="right" ID="ID_1433303632" CREATED="1311260588384" MODIFIED="1311260595386">
<node TEXT="Tabellen von Webseiten einlesen" ID="ID_1643388097" CREATED="1311260693718" MODIFIED="1311260707558">
<node TEXT="Bereits vor &quot;Projektbeginn&quot; implementiert" ID="ID_743362464" CREATED="1311261205965" MODIFIED="1311271210921"/>
<node TEXT="HTML interpretieren" ID="ID_307970224" CREATED="1311261233255" MODIFIED="1311261446762">
<node TEXT="Auf Bibliotheksfunktion aufgebaut" ID="ID_574852342" CREATED="1311261451668" MODIFIED="1311261464032"/>
</node>
<node TEXT="&#xdc;bersetzung in interne Datenstrukturen" ID="ID_1921421181" CREATED="1311261474789" MODIFIED="1311261489739">
<node TEXT="Table-Objekt" ID="ID_1452301820" CREATED="1311261490641" MODIFIED="1311261498769"/>
</node>
<node TEXT="Darstellung -&gt; GUI" ID="ID_542807151" CREATED="1311261500554" MODIFIED="1311261532205"/>
</node>
<node TEXT="GUI" ID="ID_134820875" CREATED="1311260714824" MODIFIED="1311260720160">
<node ID="ID_1226426157" CREATED="1311261673625" MODIFIED="1311261683932">
<richcontent TYPE="NODE">
<html>
  <head>
    
  </head>
  <body>
    <img src="bilder/tabellenauswerter1.png"/>
  </body>
</html>
</richcontent>
<node TEXT="Letzte Version, die der Kunde vor dem offiziellen Projektbeginn kannte" ID="ID_717943760" CREATED="1311261878150" MODIFIED="1311261924681"/>
</node>
<node TEXT="F&#xfc;r die Darstellung der Tabellen ben&#xf6;tigt" ID="ID_1583612274" CREATED="1311261693928" MODIFIED="1311261871591"/>
<node TEXT="Von Anfang an mit ber&#xfc;cksichtigt" ID="ID_1785435922" CREATED="1311262063226" MODIFIED="1311262083330"/>
<node TEXT="Musste noch erweitert und umgebaut werden" ID="ID_149340963" CREATED="1311263008669" MODIFIED="1311263037512"/>
</node>
<node TEXT="Eingelesenen Tabellen speichern" ID="ID_37713017" CREATED="1311260720582" MODIFIED="1311260730450">
<node TEXT="Musste noch implementiert werden" ID="ID_1125011329" CREATED="1311263132073" MODIFIED="1311263180056"/>
<node TEXT="Um zuk&#xfc;nftige Weiterentwicklung sicher zu stellen, musste ein Dateiformat implementiert werden" ID="ID_1792349626" CREATED="1311263303587" MODIFIED="1311263358739"/>
</node>
<node TEXT="Mehrere Tabellen einlesen und &quot;richtig zusammenf&#xfc;gen&quot;" ID="ID_898638124" CREATED="1311260736644" MODIFIED="1311260766984">
<node TEXT="-&gt; Zielbeschreibung" ID="ID_1797465055" CREATED="1311271389453" MODIFIED="1311271398537"/>
</node>
<node TEXT="Weitere Auswertung der gewonnenen Daten" ID="ID_1165394457" CREATED="1311260768812" MODIFIED="1311260955100" COLOR="#bfbfbf">
<node TEXT="Einmal pro Saison werden die Teilnehmer vom Benutzer gespeichert" ID="ID_169103065" CREATED="1311263646560" MODIFIED="1311263705378"/>
<node TEXT="Saisons werden zusammengerechnet" ID="ID_129120083" CREATED="1311263733864" MODIFIED="1311263743500">
<node TEXT="Erkennen welche Teilnehmer schon in den vorherigen Saisons vorhanden waren" ID="ID_656537395" CREATED="1311263744344" MODIFIED="1311263872415"/>
<node TEXT="Wenn ja, die Werte unter den Spalten &quot;W&quot;, &quot;D&quot;, &quot;L&quot; und &quot;Balance&quot; zusammenrechnen" ID="ID_1651333978" CREATED="1311263872845" MODIFIED="1311263952024"/>
<node TEXT="Wenn nein, Teilnehmer einfach an die Tabelle anf&#xfc;gen" ID="ID_1599025100" CREATED="1311263979687" MODIFIED="1311264002692"/>
</node>
<node TEXT="Konnte bisher nicht implementiert werden" ID="ID_682315919" CREATED="1311264026459" MODIFIED="1311264126727">
<node TEXT="Es werden mondestens die Daten von 2 Saisons ben&#xf6;tigt" ID="ID_186534451" CREATED="1311264132155" MODIFIED="1311264156706"/>
<node TEXT="Letzte Saison endete Ende Mai, n&#xe4;chste hat noch nicht angefangen" ID="ID_1992805728" CREATED="1311264158393" MODIFIED="1311264198436"/>
</node>
</node>
</node>
<node TEXT="Vorf&#xfc;hrung des Programms" POSITION="right" ID="ID_581746580" CREATED="1311267015331" MODIFIED="1311267029099"/>
<node TEXT="Fazit" POSITION="right" ID="ID_1647509658" CREATED="1311261016437" MODIFIED="1311261019389">
<node ID="ID_538736488" CREATED="1311267054460" MODIFIED="1311267077965">
<richcontent TYPE="NODE">
<html>
  <head>
    
  </head>
  <body>
    <img src="bilder/main_asian-loaded.png"/>
  </body>
</html>
</richcontent>
</node>
<node TEXT="Nicht alle Punkte aus dem Pflichtenheft konnten implementiert werden" ID="ID_1296563676" CREATED="1311266952601" MODIFIED="1311266990573"/>
<node TEXT="Aber:" ID="ID_1035008618" CREATED="1311267215043" MODIFIED="1311267220140">
<node TEXT="Wichtigste Anforderung wurde erf&#xfc;llt" ID="ID_1256783092" CREATED="1311267220967" MODIFIED="1311267248022">
<node TEXT="Daten einlesen und dauerhaft speichern" ID="ID_1845870117" CREATED="1311267256116" MODIFIED="1311267271510"/>
</node>
<node TEXT="Programm wird sowieso noch weiter entwickelt" ID="ID_1153709313" CREATED="1311267504737" MODIFIED="1311267541295"/>
</node>
<node TEXT="Qualit&#xe4;t" ID="ID_317207839" CREATED="1311269298049" MODIFIED="1311269302163">
<node TEXT="Programm ist frisch implementiert und wenig getestet" ID="ID_1883774829" CREATED="1311269324762" MODIFIED="1311269343232"/>
<node TEXT="Viele Sonderf&#xe4;lle, die bei der Benutzung auftreten k&#xf6;nnen, wurden noch nicht ber&#xfc;cksichtigt" ID="ID_1506556971" CREATED="1311272017280" MODIFIED="1311272045938">
<node TEXT="L&#xe4;uft nicht wirklich stabil" ID="ID_1721597654" CREATED="1311269428350" MODIFIED="1311269439846"/>
</node>
</node>
</node>
</node>
</map>
