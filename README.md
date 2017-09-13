# doc-mqtt
Documentationsprojekt für die MQTT-Server-VM, ActiveMQ etc.

## Was ist MQTT ?
MQTT(Message Queue Telemetry Transport) ist ein Nachrichten-Protokoll basierend auf TCP. Es zeichnet sich durch einen geringen Overhead bei der Kommunikation aus, bietet aber dennoch ein stabile Nachrichtenzustellung. Damit eignet es sich in Bereichen in denen Geräte nur über eine geringe, beziehungsweise eingeschränkte oder kostenintensive Bandbreite angebunden sind, aber dennoch regelmäßig Informationen bereitstellen bzw. beziehen sollen. Ein praktischer Anwendungsbereich, in denen MQTT bereits verbreitet eingesetzt wird, sind "Track&Trace"-Applikationen, die verschiedenste Messwerte erfassen wie Temperaturen, Drehzahlen, Wasserstände etc..
Die Geräte können dabei vom Einplatinenrechner(SoC), also beispielsweise einem Raspberry Pi der mittels GPIO um entsprechende Sensoren erweitert wurde, über Smartphones, die die entsprechenden Werte dann mobil bereitstellen, bis hin zu industriellen Fertigungsanlangen, deren Produktions- bzw Hardwarestati überwacht werden sollen, reichen.

## Wie funktioniert MQTT ?
Ein MQTT-Client kann entweder als "Listener", also als Teilnehmer der auf Nachrichten anderer MQTT-Clients hört, aber auch als "Publisher", also als Teilnehmer der Nachrichten versendet, fungieren. Die Zuordung der Nachrichten ist in Kanäle, sogenannten "topics", gegliedert, d.h. damit sich im einfachsten Falle zwei MQTT-Client "unterhalten" können, wird bei beiden dasselbe Thema ausgewählt.
Das kann im einfachsten Szenario genügen, um beispielsweise per Smartphone regelmäßige Berichte der Pegelhöhe eines Wasserkraftwerkes zugestellt zu bekommen.
Sobald aber mehrere Clients im Spiel sind und verschiedene Topic-Stränge existieren bzw. verwendet werden sollen, oder der Zugriff entsprechend gesichert werden soll, bietet es sich an, einen sogenannten "Broker", also einen MQTT-Server zu verwenden. Dieser bietet zudem die Möglichkeit weitere Protokolle, wie beispielsweise JMS(Java Messaging Service), einzubinden.

>Hinweise zur Dokumentation:
* wir verwenden für die Anbindung an Intrexx den von Apache entwickelten ActiveMQ-Server, der frei unter der Apache 2.0 Lizenz verfügbar ist.
* das im Folgenden verwendete Kürzel `<ACTIVE_MQ_INST>`  bezieht sich auf den Installtionspfad des ActiveMQ-Servers, in der von Unitplanet GmbH bereitgtestellten TestVM ist der Installationspfad `/opt/activemq`.
>

## 1) SSL-Verschlüsselung

Im Folgenden wird eine einfache Möglichkeit beschrieben, wie mit dem Java-Keytool ein selbstsigniertes Zertifikat erstellt, und dieses dann in ActiveMQ eingebunden werden kann. Hierzu muss auf dem System Java installiert und konfiguriert sein.

### a) Einen Keystore mit einem selbstsignierten Private-Key erstellen:
Zuerst erstellen wir einen Schlüsselbund(Keystore), der den privaten Schlüssel enthält:
```sh
keytool -genkey -alias amq_server -keyalg RSA -keystore amq_server.ks
```

>WICHTIG: als CN (im Dialog: "Vor- und Nachname" bzw. "First and last name") muss der FQHN der ActiveMQ-Servers übergeben werden. Es muss dann später sichergestellt werden, dass der ActiveMQ über diesen Namen erreichbar ist, damit das SSL-Handshake funktioniert.
Anfangs muss ausserdem ein Passwort für den Zugriff auf den Keystore eingegeben werden. Das später anzugebende Passwort für den Alias muss einfach mit ENTER quittiert werden, und ist somit identisch mit dem Keystore-Passwort.
Ausserdem sollte die Datei, da Sie den privaten Schlüssel des ActiveMQ enthält, entsprechend vor Zugriff geschützt werden.
>

### b) Das Zertifikat für die Clients exportieren
Aus der zuvor erstellten Keystore-Datei wird nun der öffentliche Schlüssel sowie das Zertifikat generiert:
```sh
keytool -exportcert -alias amq_server -keystore amq_server.ks -file amq_server.cert
```

### c) Das Zertifikat in Intrexx importieren
Damit Intrexx dann später eine verschlüsselte TLS-Verbindung zum ActiveMQ-Server herstellen kann, muss die gerade erstellte amq_server.cert nun in Intrexx eingebunden werden.
Hierzu muss man im Portal manager im entsprechenden Portal unter "Eigenschaften" ->  "Zertifikate" den Zertifikatsspeicher öffnen, und dort die amq_server.cert über "Import der Datei" zu den Zertifikaten hinzufügen. 
Damit die Änderung greift, muss der Portal-Dienst neu gestartet werden.

### d) SSL in ActiveMQ aktivieren und Keystore mit dem privaten Schlüssel einbinden
Hierzu muss in der <ACTIVEMQ_INST>/conf/activemq.xml im "core"-Namespace der Pfad zu dem erstellten Keystore, sowie dessen Passwort übergeben werden. Da da Passwort im Klartext vorliegt, sollte die activemq.xml entsprechend vor unberechtigtem Zugriff geschützt sein.

Auszug aus der activemq.xml:

```xml
    <broker xmlns="http://activemq.apache.org/schema/core" brokerName="localhost" dataDirectory="${activemq.data}">
...
..
.
<!-- Im sslContext muss der Pfad zur Keystore-Datei sowie das Passwort des Keystore übergeben werden -->
        <sslContext>
            <sslContext
                keyStore="/PATH/TO/amq_server.ks" keyStorePassword="GEHEIM" />
        </sslContext>

<!-- in den entsprechenden Konnektoren muss dann SSL aktiviert werden, die unbenötigten Konnektoren sollten am besten deaktiviert werden -->

        <transportConnectors>
            <!-- DOS protection, limit concurrent connections to 1000 and frame size to 100MB -->
            <!-- <transportConnector name="openwire" uri="tcp://0.0.0.0:61616?maximumConnections=1000&amp;wireFormat.maxFrameSize=104857600"/> -->
            <transportConnector name="openwire" uri="ssl://0.0.0.0:61616?maximumConnections=1000&amp;wireFormat.maxFrameSize=104857600"/>
            <transportConnector name="mqtt+ssl" uri="mqtt+ssl://0.0.0.0:8883?maximumConnections=1000&amp;wireFormat.maxFrameSize=104857600"/>
            <!-- transportConnector name="amqp" uri="amqp://0.0.0.0:5672?maximumConnections=1000&amp;wireFormat.maxFrameSize=104857600"/>
            <transportConnector name="stomp" uri="stomp://0.0.0.0:61613?maximumConnections=1000&amp;wireFormat.maxFrameSize=104857600"/>
            <transportConnector name="mqtt" uri="mqtt://0.0.0.0:1883?maximumConnections=1000&amp;wireFormat.maxFrameSize=104857600"/>
            <transportConnector name="ws" uri="ws://0.0.0.0:61614?maximumConnections=1000&amp;wireFormat.maxFrameSize=104857600"/ -->
        </transportConnectors>
```
siehe <http://activemq.apache.org/how-do-i-use-ssl.html>

### e) Den Keystore in Jetty einbinden
ActiveMQ stellt eine Weboberfläche bereit, mittels derer man sich einen Überblick über bestimmte Statusinformationen, wie beispielsweise die gerade aktiven Topics, oder auch die gerade angemeldeten Publisher/Subscriber, verschaffen kann. ActiveMQ liefert hierfür den Webserver Jetty von Apache mit aus.

Damit dieser über eine verschlüsselte HTTPS-Verbindung erreichbar ist, muss der zuvor erstellte Keystore dort ebenfalls eingebunden werden.
Hierzu gibt es in der <ACTIVEMQ_INST>/conf/jetty.xml bereits entsprechende, aber noch auskommentierte Einträge, welche, wie zuvor bereits im ActiveMQ entsprechend, um Pfad und Passwort des Keystores erweitert werden müssen:

```xml
        <!--
            Enable this connector if you wish to use https with web console
        -->
        <bean id="SecureConnector" class="org.eclipse.jetty.server.ServerConnector">
            <constructor-arg ref="Server" />
            <constructor-arg>
                <bean id="handlers" class="org.eclipse.jetty.util.ssl.SslContextFactory">
                    <property name="keyStorePath" value="/PATH/TO/amq_server.ks" />
                    <property name="keyStorePassword" value="GEHEIM" />
                </bean>
            </constructor-arg>
            <property name="port" value="8162" />
        </bean>
```

Damit die Umleitung von HTTP auf HTTPS funktioniert, muss dann noch ein entsprechender Eintrag in der web.xml vorgenommen werden.
Dies wird im Abschnitt "Redirecting http requests to https" in der Jetty-Dokumentation beschrieben:

<https://wiki.eclipse.org/Jetty/Howto/Configure_SSL>

### Hinweis zur Verwendung eines offiziell signierten Zertifikates
Die oben genannten Punkte beschreiben die einfachste Vorgehensweise über ein selbsigniertes Zertifikat. Der Vorteil dabei ist, dass man die Verbindung auf einfache Weise verschlüsseln kann. Da das Zertifikat aber selbstsigniert ist, und eben nicht von einer offiziellen Zertifikatsstelle (CA Authority) signiert wurde ist die Vertrauenskette (Chain of Trust) nicht gewährleistet. Das führt beispiesweise dazu, dass im Webbrower beim Zugriff auf die ActiveMQ Webmin-Oberfläche ein Warnhinweis erscheint, da der Ersteller nicht bekannt ist.

Falls offiziell signierte Zertifikate erstellen möchte, wäre die Vorgehensweise wie folgt:
* man erstellt einen privaten Schlüssel
* generiert daraus eine Zertifikatsanforderung
* lässt diese dann von einer offiziellen Zertifizierungsstelle signieren

Die dann von der Zertifizierungsstelle zurückerhaltenen, signierten Zertifikate liegen meist in unterschiedlichen Formaten vor.
Am Einfachsten lassen sich die Zertifikate im PEM-Format (im Klartext) einbinden, indem man die entsprechenden Dateien mit einem Texteditor öffnet, den privaten Schlüssel, Zertifikate sowie Zwischenzertifikate kopiert und daraus eine neue Datei, welche die komplette Kette enthält, generiert, also:

a) Man erstellt eine neue Textdatei "zertifikatskette.pem" in die per Copy&Paste der private Schlüssel, sowie sämtliche Zertifikate inklusive BEGIN/END-Prolog eingetragen werden:

Der private Schlüssel (bspw. *.key):
```sh
-----BEGIN RSA PRIVATE KEY-----
...
```

Das Zertifikat (bspw. *.crt):
```sh
-----BEGIN CERTIFICATE-----
...
```
Und eventuelle CA-Zwischenzertifikate (bspw. *.ca):
```sh
-----BEGIN CERTIFICATE-----
...
```

b) Danach wird diese pem-Datei über den folgenden Befehl nach pkcs12 konvertiert (OpenSSL muss installiert sein):
```sh
openssl pkcs12 -export -name MY_ALIAS -in zertifikatskette.pem -out zertifikats_keystore.p12
```

c) Die Einbindung in ActiveMQ bzw. Jetty funktioniert wie in Punkt d) bzw. e) beschrieben, da der gerade erzeugte Keystore vom Typ PKCS12 ist, muss dies in der Einbindung explizit mitangegeben werden:

In der jetty.xml:
```xml                                                     
        <property name="keyStorePath" value="/PATH/TO/zertifikats_keystore.p12" />
        <property name="keyStorePassword" value="GEHEIM" />
        <property name="keyStoreType" value="pkcs12" />
```
In der activemq.xml im sslContext:
```xml
        <sslContext>
            <sslContext
                keyStore="/PATH/TO/zertifikats_keystore.p12" keyStorePassword="GEHEIM" keyStoreType="pkcs12" />
        </sslContext>
```

## 2) Einrichtung der Benutzer

### a) Benutzer der Jetty-Webmin
Die Benutzer, die sich an der Webmin-Oberfläche anmelden dürfen, werden in der  <ACTIVEMQ_INST>/conf/jetty-realm.properties definiert.

### b) Benutzerberechtigungen der Konnektoren
Die einfachste Möglichkeit ist das direkte Setzen der Berechtigungen in der activemq.xml mittels des "SimpleAuthenticationPlugin". Über einen entsprechenden authentication-Eintrag fügt man einen neuen Benutzer, sowie Passwort und die Gruppenzugehörigkeit hinzu.

Über das authorizationPlugin können dann die Berechtigungen an den Topics/Queues den Benutzern zugewiesen werden. Read- bzw. Write-Permissions dürften selberklärend sein. Die "admin"-Rolle beschreibt in dem Zusammenhang die Rechte ein Topic zu erstellen.

```xml
    <plugins>
        <simpleAuthenticationPlugin anonymousAccessAllowed="false">
            <users>
                <authenticationUser username="admin" password="admin"
                groups="admins,publishers,consumers"/>
                <authenticationUser username="user_publ" password="admin"
                groups="publishers"/>
                <authenticationUser username="user_cons" password="admin"
                groups="consumers"/>
            </users>
        </simpleAuthenticationPlugin>

        <authorizationPlugin>
            <map>
                <authorizationMap>
                    <authorizationEntries>
                        <authorizationEntry topic=">"
                            read="admins" write="admins" admin="admins" />
                        <authorizationEntry topic="ActiveMQ.Advisory.>"
                            read="publishers,consumers" write="publishers,consumers" admin="admins,consumers,publishers" />
                        <authorizationEntry topic="test-mqtt.>"
                            read="consumers" write="publishers"
                            admin="admins" />
                    </authorizationEntries>
                </authorizationMap>
            </map>
        </authorizationPlugin>
    </plugins>
```

Weitere Informationen hierzu unter:
<http://activemq.apache.org/security.html>
<http://activemq.apache.org/wildcards.html>

#### Hinweis
ActiveMQ bietet die Möglichkeit, Informationen über die Topics über den ActiveMQ.Advisory-Zweig zur Verfügung zu stellen, bspw. wird beim Verbindungsaufbau eines Clients im ActiveMQ.Advisory.Connection-Zweig eine Message generiert. Falls man die dort bereitsgestellten Informationen benötigt, benötigt der Client auch dort die notwendigen Lese-/Schreibberechtigungen. Falls die entsprechenden Zweige nicht vorhanden sind, benötigt der Client dann auch Admin-Berechtigungen um die Topics generieren zu können bzw. muss zuvor sichergestellt werden, dass die benötigen Advisory topics vorhanden sind.

Über den folgenden Eintrag im Broker-Namespace der activemq.xml lassen sich die Advisory Messages aber auch deaktivieren:
```xml
<broker advisorySupport="false">
```
siehe auch:
<http://activemq.apache.org/advisory-message.html#AdvisoryMessage-Disablingadvisorymessages>


## 3) Berechtigungen sicherstellen und Dienst neu starten

Der ActiveMQ-Server läuft unter einem restrictiven Benutzer-Account "activemq", deshalb muss nach den in 1) und 2) vorgenommenen Änderungen sichergestellt werden, dass Besitzer und Gruppenzugehörigkeit der geänderten Dateien noch stimmen, d.h. Besitzer und Gruppenzugehörigkeit der Datei müssen beide "activemq" lauten.

Über folgenden Befehl lässt sich das kontrollieren:
```sh
ls -la /opt/activemq/conf/activemq.xml /opt/activemq/conf/jetty.xml

-rw-r--r-- 1 activemq activemq 7785 2017-03-20 08:14 /opt/activemq/conf/activemq.xml
-rw-r--r-- 1 activemq activemq 7841 2017-03-15 16:04 /opt/activemq/conf/jetty.xml
```

Dasselbe gilt für die in Punkt 1) erstellte Keystore-Datei. Der Speicherpfad der Datei und Benutzer/Gruppe müssen entsprechend vom activemq-Benutzer gelesen werden können.

Korrigieren ließe sich das über den folgenden Befehl:
```sh
chown activemq.activemq <DATEINAME>
```

Danach muss der ActiveMQ-Dienst neu gestartet werden:
```sh
service activemq restart
```

