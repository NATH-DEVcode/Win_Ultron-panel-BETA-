# ULTRON Panel para Windows

Aplicación de escritorio ULTRON CORE para Windows.

⚠️ **Esta versión está en fase beta.** Puede tener fallos, carecer de funciones,
colgarse o presentar problemas de compatibilidad.

## Instalar e iniciar

Ejecuta `INSTALAR-ULTRON-WINDOWS.bat` y luego
`INICIAR-ULTRON-WINDOWS.bat`.

## API key de Groq

La API key se configura dentro de ULTRON por usuario. Al abrir **Conciencia**,
si ese usuario todavía no tiene una clave, ULTRON ofrece abrir Groq para crear
una. La clave se guarda en el administrador de credenciales de Windows cuando
está disponible. Si no hay un almacén compatible, se cifra localmente con
DPAPI. El diálogo indica dónde se guardó.

## Comandos por voz y alertas

Las aplicaciones, sitios web y umbrales del monitor se editan en
`config/ultron_features.json`. Guarda el archivo y reinicia ULTRON para aplicar
los cambios. Usa el botón **MIC · F8** o la tecla **F8** para activar y detener
la escucha. La lista inicial incluye herramientas de Windows, navegadores,
Office, Spotify, Discord, Zoom, VLC y Visual Studio Code. En Windows también
puedes decir «abre [nombre de una aplicación instalada]» para pedirle al menú
de aplicaciones que la localice. Para máxima compatibilidad, agrega la app y
su comando al JSON; los destinos desconocidos nunca se ejecutan como comandos
de terminal.

## Recuperación y registros

En el primer inicio de una cuenta nueva, guarda el código de recuperación que
ULTRON muestra. Permite restablecer la contraseña si se olvida. El registro de
inicio, cuando ULTRON se ejecuta sin consola, está en
`%USERPROFILE%\.ultron\startup.log`.
