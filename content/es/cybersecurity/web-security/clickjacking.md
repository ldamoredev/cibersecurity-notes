# Clickjacking

## Definición

Clickjacking es un ataque de redirección de UI donde un atacante embebe una página objetivo en un frame y engaña al usuario para que haga clic o escriba en la UI real del objetivo mientras cree que está interactuando con otra página.

La vulnerabilidad no es "una página tiene botones." La vulnerabilidad es que una página sensible puede ser embebida por un origen no confiable y manipulada visualmente alrededor de la sesión del usuario.

## Por qué importa

Clickjacking convierte el comportamiento normal de framing del navegador en un canal de acciones del usuario confundido. Si un usuario con sesión iniciada puede ser atraído a una página del atacante, el atacante puede causar cambios de cuenta, otorgamiento de consentimiento, acciones de pago, clics destructivos en el admin, o acciones de UI que impacten la privacidad.

Está estrechamente conectado con [[content-security-policy]] porque la protección moderna suele ser `Content-Security-Policy: frame-ancestors ...`. También toca [[csrf]] porque ambas clases abusan del navegador de un usuario autenticado, pero no son el mismo bug: CSRF envía un request; clickjacking manipula la interacción visible.

## Cómo funciona

Clickjacking tiene **5 partes móviles**:

1. **Página objetivo sensible.** La víctima está autenticada en una página con acciones de UI significativas.
2. **Wrapper controlado por el atacante.** El atacante hospeda una página que embebe el objetivo en un `<iframe>`.
3. **Engaño visual.** Opacidad CSS, posicionamiento, overlays o texto engañoso ocultan en qué está haciendo clic realmente el usuario.
4. **Acción del usuario.** La víctima hace clic, arrastra, escribe o toca donde el atacante quiere.
5. **El navegador envía la interacción confiable.** La acción cae en la página objetivo enmarcada bajo la sesión de la víctima.

Forma mínima del wrapper:

```
<style>
iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 800px;
  height: 600px;
  opacity: 0.05;
  z-index: 2;
}
.bait {
  position: absolute;
  top: 140px;
  left: 220px;
  z-index: 1;
}
</style>
<button class="bait">Reclamar recompensa</button>
<iframe src="https://target.example/account/delete"></iframe>
```

El bug no es la etiqueta iframe. El bug es la ausencia o el exceso de permisividad en el control de embebido de una página cuya UI puede causar cambios de estado sensibles.

## Técnicas / patrones

Los atacantes y testers miran:

- páginas de configuración de cuenta, restablecimiento de contraseña, cambio de email, MFA, consentimiento OAuth, facturación, admin y acciones destructivas
- páginas que se renderizan mientras se está autenticado y no tienen header anti-framing
- acciones que cambian estado que dependen solo de un clic o interacción de formulario simple
- confirmaciones de un solo clic y diálogos de confirmación débiles
- protección mixta donde algunas páginas establecen `frame-ancestors` y otras no
- flujos de portal o de partner donde el embebido legítimo es necesario pero demasiado ampliamente permitido

### Ejemplo trabajado: capacidad de framing de página sensible

```
Objetivo:
  /account/email

Acción:
  cambiar el email de recuperación

Headers:
  sin Content-Security-Policy frame-ancestors
  sin X-Frame-Options

Test:
  página wrapper propia embebe /account/email mientras está autenticado

Decisión:
  el riesgo de clickjacking es real si la UI enmarcada puede completar el cambio o iniciar un flujo sensible
```

Un buen hallazgo establece tanto la capacidad de framing como la acción del usuario que se vuelve peligrosa.

## Variantes y bypasses

Clickjacking tiene **5 variantes prácticas**.

### 1. iframe transparente clásico

La página objetivo se coloca sobre un señuelo controlado por el atacante con baja opacidad o posicionamiento cuidadoso. La víctima hace clic en la UI real del objetivo.

### 2. Engaño de cursor o puntero

El atacante usa estilos y diseño para que el puntero parezca alineado con una acción falsa mientras el clic real cae en otro lugar.

### 3. Redirección de UI en múltiples pasos

El atacante guía al usuario a través de varios clics de aspecto inofensivo que se alinean con un flujo sensible de múltiples pasos dentro del frame.

### 4. Abuso de arrastrar-y-soltar o escritura

Algunas acciones de UI no son simples clics. El ataque puede engañar a los usuarios para que arrastren datos, seleccionen opciones, o escriban en un objetivo enmarcado.

### 5. Framing de confianza demasiado amplio

El sitio usa `frame-ancestors` pero permite orígenes amplios de partner, wildcard, o legados que pueden hospedar páginas controladas por el atacante.

## Impacto

Ordenado aproximadamente por severidad:

- **Cambios de cuenta o configuración de seguridad.** Email, MFA, contraseña, sesión o configuraciones de recuperación pueden ser alterados.
- **Abuso de autorización o consentimiento.** Páginas de OAuth, SSO, autorización de app o consentimiento de administrador pueden ser manipuladas.
- **Acciones financieras o destructivas.** Pagos, compras, eliminaciones y cambios administrativos pueden desencadenarse.
- **Exposición de privacidad.** La UI enmarcada puede revelar estado o engañar a los usuarios para que compartan información.
- **Erosión de confianza.** Incluso los intentos fallidos socavan la confianza en los flujos de trabajo sensibles.

El impacto depende de la página enmarcada, el rol del usuario, si la acción requiere autenticación reciente, y si la UI objetivo tiene confirmación independiente.

## Detección y defensa

Ordenado por efectividad:

1.
**Establecer `Content-Security-Policy: frame-ancestors` en páginas sensibles.**
   `frame-ancestors 'none'` bloquea todo framing; `frame-ancestors 'self'` limita el framing a páginas del mismo origen. Este es el control moderno y expresivo del navegador y debería desplegarse en las respuestas que necesitan protección.

2.
**Usar `X-Frame-Options` para cobertura en navegadores legacy donde sea apropiado.**
   `DENY` y `SAMEORIGIN` son más simples que CSP y menos flexibles, pero siguen siendo útiles para clientes más antiguos. No depender de `ALLOW-FROM`; el soporte es inconsistente y obsoleto.

3.
**Requerir confirmación fuerte para acciones de alto riesgo.**
   Re-autenticación, confirmación escrita, MFA step-up y firma de transacciones reducen el daño cuando se expone una UI. Estos controles deberían complementar el bloqueo de frames, no reemplazarlo.

4.
**Mantener el embebido legítimo acotado y explícito.**
   Si los partners o portales internos deben enmarcar una página, permitir solo orígenes exactos de confianza y revisar si esos orígenes pueden hospedar contenido controlado por el atacante.

5.
**Testear cada ruta sensible, no solo la homepage.**
   Los middlewares de headers, rutas de proxy, páginas de error estáticas y flujos legacy suelen diverger. La protección contra clickjacking es por respuesta.

### Qué no funciona como defensa primaria

- **Solo tokens CSRF.** Clickjacking usa el navegador real del usuario y la UI real, por lo que pueden estar presentes tokens CSRF válidos.
- **Frame-busting con JavaScript.** Los scripts pueden fallar, ser bloqueados, generar race conditions, o quedar en sandbox; los headers son el control primario.
- **Ocultar botones con CSS.** El atacante controla la página wrapper, no la presentación segura del objetivo.
- **Solo proteger la página de login.** El riesgo suele estar en páginas de configuración autenticadas, consentimiento, facturación y admin.

## Labs prácticos

Usá apps propias o labs intencionalmente vulnerables.

### Inspeccionar las protecciones de frame

```
curl -I https://app.example.test/account/settings | rg -i "content-security-policy|x-frame-options"
```

Buscar específicamente `frame-ancestors` en CSP o `DENY` / `SAMEORIGIN` en `X-Frame-Options`.

### Construir un test de frame local

```
<!doctype html>
<html>
  <body>
    <h1>Frame test</h1>
    <iframe src="https://app.example.test/account/settings" width="900" height="700"></iframe>
  </body>
</html>
```

Abrir este archivo localmente mientras se está autenticado en la app objetivo y confirmar si el navegador bloquea el framing.

### Comparar rutas sensibles y no sensibles

```
for path in / /account /account/settings /admin /oauth/authorize; do
  printf "\n== %s ==\n" "$path"
  curl -skI "https://app.example.test$path" | rg -i "content-security-policy|x-frame-options" || true
done
```

La protección debería ser consistente en las rutas sensibles, no solo en la página raíz.

### Verificar los ancestros permitidos

```
Ruta:
Valor de frame-ancestors:
Orígenes permitidos:
¿Los orígenes permitidos hospedan contenido de usuario?:
Acción sensible disponible:
Decisión:
```

Una allowlist es tan fuerte como el origen permitido menos confiable.

### Registrar un hallazgo de clickjacking

```
Página:
Rol del usuario:
Acción sensible:
Protección de frame observada:
Wrapper de prueba:
Acción completada o parcialmente completada:
Header recomendado:
Resultado del retest:
```

Evitar pruebas destructivas. Demostrar la capacidad de framing y elegir una acción inofensiva o reversible.

## Ejemplos prácticos

- La configuración de cuenta puede enmarcarse y un usuario con sesión iniciada puede ser engañado para iniciar un flujo de cambio de email.
- Una página de consentimiento OAuth es enmarcable y puede alinearse debajo de una UI "continuar" engañosa.
- Un panel de administración bloquea el framing, pero un endpoint de acción de admin legacy no lo hace.
- Una página de confirmación de pago usa tokens CSRF pero carece de `frame-ancestors`, permitiendo la redirección de UI.
- Un portal de partner requiere framing, pero `frame-ancestors *` permite que cualquier sitio embeba la página.

## Notas relacionadas

- [[content-security-policy]]
- [[csrf]]
- [[http-headers]]
- [[xss]]
- [[open-redirect]]
- [[auth-flaws]]

## Referencias

- **Fundamental:** MDN CSP `frame-ancestors` — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors
- **Fundamental:** OWASP Clickjacking Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Clickjacking — https://portswigger.net/web-security/clickjacking
