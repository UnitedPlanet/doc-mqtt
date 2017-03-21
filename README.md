# doc-mqtt
Documentationsprojekt für MQTT-Server-VM, ActiveMQ etc.

Hinweise zur Doku:
* der PATH-Environment muss gesetzt sein, siehe
https://www.java.com/de/download/help/path.xml
* der Installationspfad <ACTIVE_MQ_INST> liegt in der TestVM unter /opt/activemq

## 1) SSL-Verschlüsselung

Im Folgenden wird eine einfache Möglichkeit beschrieben, wie mit dem Java-Keytool ein selbstsigniertes Zertifikat erstellt, und dieses dann in ActiveMQ eingebunden werden kann.

### a) Einen Keystore mit einem selbstsignierten Private-Key erstellen:

```sh
keytool -genkey -alias amq_server -keyalg RSA -keystore amq_server.ks
```

>WICHTIG: als CN (im Dialog: "Vor- und Nachname" bzw. "First and last name") muss der FQHN der ActiveMQ-Servers übergeben werden. Es muss dann später sichergestellt werden, dass der ActiveMQ über diesen Namen erreichbar ist, damit das SSL-Handshake funktioniert.
Anfangs muss ausserdem ein Passwort für den Zugriff auf den Keystore eingegeben werden. Das später anzugebende Passwort für den Alias muss einfach mit ENTER quittiert werden, und ist somit identisch mit dem Keystore-Passwort.
>

### b) Das Zertifikat für die Clients exportieren
```sh
keytool -export -alias amq_server -keystore amq_server.ks -file amq_server.cert
```

### c) Das Zertifikat in Intrexx importieren
Auf Intrexx-Seite muss nun das Zertifikat amq_server.cert in den Portal-Eigenschaften unter "Zertifikate" den Zertifikatsspeicher öffnen, und dort diese mittels "Import der Datei" hinzufügen. Danach muss der Portal-Dienst neu gestartet werden.

### d) SSL in ActiveMQ aktivieren und Keystore einbinden
Hierzu in der <ACTIVEMQ_INST>/conf/activemq.xml im "core"-Namespace der Pfad zu dem erstellten Keystore sowie dessen Passwort übergeben werden. Da da Passwort im Klartext vorliegt, sollte die activemq.xml entsprechend vor unberechtigtem Zugriff geschützt sein.

Auszug aus der activemq.xml:

```xml
    <broker xmlns="http://activemq.apache.org/schema/core" brokerName="localhost" dataDirectory="${activemq.data}">
...
..
.
<!-- Hier der Pfad und Passwort des Keystore-Files -->
            <sslContext>
              <sslContext
                    keyStore="/PATH/TO/broker.ks" keyStorePassword="GEHEIM" />
            </sslContext>

<!-- in den entsprechenden Konnektoren SSL aktivieren, unbenötigte Konnektoren deaktivieren -->

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
siehe http://activemq.apache.org/how-do-i-use-ssl.html

### e) Den Keystore in Jetty einbinden
ActiveMQ verwendet für seine Webadmin-Oberfläche Apache Jetty. Damit diese über eine verschlüsselte HTTPS-Verbindung erreichbar ist, muss der zuvor erstellte Keystore dort ebenfalls eingebunden werden.
Hierzu gibt es in der <ACTIVEMQ_INST>/conf/jetty.xml bereits entsprechende - aber noch auskommentierte - Einträge, zuvor in der activemq.xml muss Pfad und Passwort des Keystores hinterlegt werden:

```xml
                <!--
                    Enable this connector if you wish to use https with web console
                -->
                <bean id="SecureConnector" class="org.eclipse.jetty.server.ServerConnector">
                                        <constructor-arg ref="Server" />
                                        <constructor-arg>
                                                <bean id="handlers" class="org.eclipse.jetty.util.ssl.SslContextFactory">

                                                        <property name="keyStorePath" value="/PATH/TO/broker.p12" />
                                                        <property name="keyStorePassword" value="GEHEIM" />
                                                </bean>
                                        </constructor-arg>
                                        <property name="port" value="8162" />
                                </bean>
```

Damit die Umleitung von HTTP auf HTTPS funktioniert, muss dann noch ein entsprechender Eintrag in der web.xml vorgenommen werden.
Dies wird im Abschnitt "Redirecting http requests to https" in der Jetty-Dokumentation beschrieben:

https://wiki.eclipse.org/Jetty/Howto/Configure_SSL

## 2) Einrichtung der Benutzer

### a) Benutzer der Jetty-Webmin
Die Benutzer, die sich an der Webmin-Oberfläche anmelden dürfen, werden in der  <ACTIVEMQ_INST>/conf/jetty-realm.properties definiert.

### b) Benutzerberechtigungen der Konnektoren
Die einfachste Möglichkeit ist das direkte Setzten der Berechtigungen in der activemq.xml mittels des SimpleAuthenticationPlugin:
Über einen entsprechenden authentication-Eintrag fügt man einen neuen Benutzer, sowie Passwort und die Gruppenzugehörigkeit hinzu.

Über das authorizationPlugin können dann die Berechtigungen an den Topics/Queues den Benutzern zugewiesen werden. Read- bzw. Write-Permissions dürften selberklärend sein. Die "admin"-Rolle beschreibt in dem Zusammenhang die Rechte ein Topic zu erstellen.

>Wichtig: Um auf ein beliebiges Topic lesend bwz. schreibend zugreifen zu können benötigt der Benutzer "admin"-Berechtigungen am "ActiveMQ.Advisory.>"-Zweig, da dort Informationen wie bspw. bestehende Verbindungen u.ä. gespeichert werden.
>

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

Weitere Info unter:
http://activemq.apache.org/security.html
http://activemq.apache.org/wildcards.html