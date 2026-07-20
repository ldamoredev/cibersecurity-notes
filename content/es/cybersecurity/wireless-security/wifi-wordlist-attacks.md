# Wi-Fi Wordlist Attacks

## Definición

Los ataques de wordlist Wi-Fi testean material WPA/WPA2-PSK capturado contra passphrases candidatas para determinar si una clave de red es adivinable.

## Por qué importa

La captura inalámbrica es solo la mitad de la historia. El testing por wordlist muestra si el PSK elegido por humanos es suficientemente débil para recuperarse offline.

Esta nota pertenece a la seguridad inalámbrica porque el input es material de handshake Wi-Fi, pero la lección más profunda se transfiere a todas partes: los secretos compartidos fallan cuando los humanos eligen palabras, formatos y mutaciones predecibles.

## Cómo funciona

Los ataques de wordlist tienen **5 etapas**:

1. **Adquirir material válido.** Capturar un handshake o PMKID de una red propia o autorizada.
2. **Elegir fuentes candidatas.** Usar defaults conocidos, patrones de política o diccionarios de prueba.
3. **Aplicar reglas o máscaras.** Generar variaciones realistas.
4. **Derivar y comparar.** La herramienta testea candidatas contra el material capturado.
5. **Reportar la fortaleza.** Una captura no crackeada no es prueba de fortaleza, solo prueba contra las candidatas testeadas.

El bug no es que exista el testing offline. El bug es un PSK que aparece en un conjunto de candidatas realista.

Un ejemplo trabajado, resultado de wordlist sin exagerar:

```
Captura:
  WPA2 handshake del lab

Conjunto de candidatas:
  nombres de empresa, estaciones del año, años, patrones de guest, 500 entradas de prueba

Resultado:
  sin coincidencia

Conclusión:
  el PSK resistió solo este conjunto de candidatas; no es prueba de aleatoriedad fuerte

Próxima acción:
  verificar longitud generada, almacenamiento, separación de guest y proceso de rotación
```

Un test de crackeo fallido debería acotar las conclusiones, no crear falsa confianza.

## Técnicas / patrones

El testing evalúa:

- contraseñas predeterminadas de router y patrones de ISP
- nombres de empresa, direcciones, estaciones y sufijos predecibles
- contraseñas de guest reutilizadas
- passphrases cortas con sustituciones
- si se usan gestores de contraseñas o secretos generados

## Variantes y bypasses

El testing por wordlist tiene **4 modos comunes**.

### 1. Diccionario directo

Testea cada candidata exactamente como está escrita.

### 2. Mutación basada en reglas

Aplica edits predecibles como años, capitalización y símbolos.

### 3. Ataque de máscara

Testea un patrón estructurado como letras más dígitos.

### 4. Guessing informado por objetivo

Usa palabras específicas de la organización, lo que genera preocupaciones éticas y de privacidad y debe mantenerse dentro de la autorización.

## Impacto

Ordenado aproximadamente por severidad:

- **Recuperación del PSK.** Una candidata que coincide revela el secreto de red compartido.
- **Acceso futuro silencioso.** La clave puede reutilizarse hasta la rotación.
- **Riesgo de credenciales más amplio.** Las contraseñas Wi-Fi predecibles pueden indicar problemas de cultura de contraseñas más amplios.
- **Falsa confianza.** Un crackeo fallido puede malinterpretarse como prueba de seguridad fuerte.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar PSKs generados, largos y aleatorios.**
   La aleatoriedad hace que las estrategias de wordlist y máscara sean impracticables a escalas normales.

2.
**Migrar entornos de alta confianza a autenticación Enterprise.**
   Las credenciales y certificados por usuario reducen el blast radius del secreto compartido.

3.
**Rotar PSKs compartidos cuando cambia la membresía.**
   Los secretos compartidos se vuelven obsoletos cuando personas y dispositivos se van.

4.
**Testear contra conjuntos de candidatas realistas durante auditorías.**
   El testing defensivo detecta contraseñas que el texto de la política sola se pierde.

### Qué no funciona como defensa primaria

- **Agregar `!` o `2026` a una palabra.** Esas mutaciones son exactamente lo que testean las reglas.
- **Asumir que una wordlist fallida significa seguro.** Solo significa que ese conjunto de candidatas falló.
- **Usar nombres de la organización en PSKs.** Las palabras específicas del contexto son candidatas fáciles.
- **Depender de lockouts.** El guessing offline de WPA/WPA2 no golpea el AP después de la captura.

## Labs prácticos

Usar solo handshakes de redes lab propias.

### Crear un conjunto de candidatas defensivas pequeño

```
nombredempresa2026!
guestwifi2026
labrouter12345
correct-horse-battery-staple
```

Usar esto para demostrar por qué los patrones predecibles son peligrosos.

### Ejecutar una verificación acotada del lab

```
aircrack-ng -w lab-wordlist.txt -b LAB_BSSID wpa-lab-01.cap
```

Registrar si el PSK coincidió con las candidatas testeadas.

### Reportar sin exagerar

```
Captura:
Conjunto de candidatas:
Reglas/máscaras:
Resultado:
Qué prueba esto:
Qué no prueba esto:
```

El crackeo fallido es evidencia limitada, no una garantía.

### Comparar modelos de PSK humano y generado

```
Fuente PSK | longitud | patrón | rotación | ¿probable en wordlists? | decisión
frase humana | 14 | marca+año | anual | sí | reemplazar
generado | 24 | aleatorio | al irse | no | mantener
```

El objetivo defensivo es eliminar candidatas predecibles.

### Documentar el manejo seguro de capturas

```
archivo de captura:
contiene identificadores de clientes:
ubicación de almacenamiento:
período de retención:
fecha de borrado:
scope autorizado:
```

Las capturas inalámbricas pueden contener metadatos sensibles y deberían retenerse deliberadamente.

## Ejemplos prácticos

- Una contraseña de Wi-Fi guest es el nombre de la empresa más el año actual.
- La clave predeterminada de un router sigue un patrón del vendor.
- Un PSK del lab se crackea con un diccionario de cinco líneas.
- Una passphrase larga y generada sobrevive un conjunto de auditoría realista.
- Un PSK compartido sigue siendo válido después de una rotación de personal.

## Notas relacionadas

- [[wpa-wpa2-handshakes]]
- [[wireless-security]]
- [[wep-security]]
- [[token-lifecycle|Token Lifecycle]]
- [[scope-validation|Scope Validation]]

### Notas atómicas futuras sugeridas

- password-cracking-rules
- hashcat-workflows
- wireless-key-rotation
- default-router-credentials

## Referencias

- **Docs Oficiales:** Aircrack-ng WPA/WPA2 tutorial — https://www.aircrack-ng.org/doku.php?id=cracking_wpa
- **Docs Oficiales:** Hashcat example hashes — https://hashcat.net/wiki/doku.php?id=example_hashes
- **Mitigación:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
