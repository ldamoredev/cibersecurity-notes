# Traffic Correlation

## Definición

La correlación de tráfico es la vinculación de la actividad de un usuario comparando el timing de tráfico, volumen, ruteo y patrón entre diferentes puntos de observación.

## Por qué importa

Incluso cuando el contenido está cifrado y la IP de origen está oculta, un observador con suficiente visibilidad puede a veces comparar cuándo entran los paquetes y cuándo salen. Tor y otros sistemas de anonimato están diseñados en parte para hacer esto más difícil, pero la correlación de tráfico sigue siendo una preocupación central de anonimato.

## Cómo funciona

Usá las 5 señales de tráfico:

1.
**Timing**
   Cuándo aparecen los paquetes y cómo se alinean.

2.
**Volumen**
   Cuántos datos se mueven en cada dirección.

3.
**Dirección**
   Hacia dónde fluyen los paquetes y cómo se alinean los bursts.

4.
**Ruta**
   Qué relays, proveedores o redes están en la ruta.

5.
**Patrón**
   Estructura repetida en el flujo de tráfico.

El bug no es que exista tráfico. El bug es asumir que el cifrado solo oculta el timing y el volumen.

## Técnicas / patrones

- Usar sistemas de anonimato que distribuyan la confianza y mezclen los patrones de tráfico.
- Evitar patrones de actividad únicos cuando el anonimato importa.
- Tratar las cargas grandes, los bursts distintivos y el timing regular como vinculables.
- Reconocer que los logs del lado del servidor y las observaciones del lado de la red pueden combinarse.
- Entender que los exits públicos, bridges y puntos de entrada crean diferentes puntos de visibilidad.

## Variantes y bypasses

Usá las 6 formas de correlación:

### 1. Timing de extremo a extremo

Comparar cuándo el tráfico entra y sale de una red.

### 2. Correlación de bursts

Hacer coincidir picos o pausas distintivas.

### 3. Correlación de patrón interactivo

El cadencia de chat o navegación puede revelar la forma de una sesión.

### 4. Correlación de sitio web y relay

Diferentes observadores en la ruta pueden combinar vistas parciales.

### 5. Correlación de patrón de tamaño de paquetes

Las secuencias de tamaño repetidas pueden ser identificadoras.

### 6. Correlación entre sesiones

La misma rutina entre múltiples sesiones se vuelve vinculable.

## Impacto

- Los adversarios fuertes pueden vincular origen y destino a pesar del cifrado.
- Los patrones de timing y tamaño pueden debilitar el anonimato.
- La visibilidad de entrada y salida de Tor importa de manera diferente a la privacidad de VPN ordinaria.
- Los flujos de trabajo únicos son más fáciles de correlacionar.
- Los usuarios pueden asumir que "cifrado" significa "no correlacionable", lo cual es falso.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar un diseño que reduzca el poder de un único observador**
   La estructura de relays de Tor existe por esta razón.

2.
**Evitar patrones de tráfico distintivos**
   Las transferencias grandes, rítmicas o únicas son más fáciles de hacer coincidir.

3.
**Separar actividades en tiempo y contexto**
   Una identidad no debería crear un patrón repetible entre tareas no relacionadas.

4.
**Usar bridges y camuflaje de transporte donde sea necesario**
   Esto ayuda contra la detección local, no contra la resistencia a la correlación total.

5.
**Asumir que los observadores fuertes pueden combinar datos parciales**
   El modelo seguro es conservador.

### Qué no funciona como defensa primaria

- **El cifrado no detiene la correlación de tráfico.**
- **Una VPN no elimina los patrones de timing.**
- **Tor reduce pero no elimina el riesgo de correlación.**
- **Las pausas aleatorias y trucos ad hoc no son una estrategia robusta de anonimato.**

## Labs prácticos

### Dibujar un boceto de timing

```
Evento 1:
Evento 2:
Evento 3:
Burst de paquetes:
Pausa:
El observador A ve:
El observador B ve:
Vínculo posible:
```

El boceto revela oportunidades de correlación.

### Comparar patrones de volumen

```
Tamaño de carga:
Tamaño de descarga:
Forma del burst:
Repetibilidad:
¿Distintivo?
```

Los patrones distintivos son patrones vinculables.

### Revisar la visibilidad de la ruta

```
Observador:
Ve la entrada:
Ve la salida:
Ve el timing:
Ve el volumen:
Puede combinar con:
```

Esta es la tabla central de correlación de tráfico.

### Identificar flujos de trabajo de alto riesgo

```
Flujo de trabajo:
Chat / navegación / carga / descarga:
Regularidad:
Sensibilidad:
Necesidad de anonimato:
Riesgo de patrón:
```

Algunos flujos de trabajo son inherentemente más fáciles de correlacionar que otros.

## Ejemplos prácticos

- Un patrón de carga y descarga de archivos grandes es fácil de detectar en una red.
- Una sesión de Tor sigue teniendo estructura de timing y tamaño de paquetes.
- Una VPN oculta la IP de origen pero no todas las características de flujo.
- Un horario diario repetido se convierte en una pista de correlación.
- Un bridge o transporte ayuda con la detección de censura pero no con todos los observadores globales.

## Notas relacionadas

- [[anonymity-threat-models|Anonymity Threat Models]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[vpn-vs-tor|VPN vs Tor]]
- [[deanonymization-failures|Deanonymization Failures]]
- [[packet-analysis|Packet Analysis]]

## Referencias

- **Investigación / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
