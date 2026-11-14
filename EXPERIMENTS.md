# Experimentos independientes de sólo lectura

El método de este documento es **no oficial**: sirve para estudiar y comparar lo que el Go reporta, no para desactivar Secure Boot. No carga imágenes personalizadas, no cambia el bloqueo ni intenta alterar la cadena de confianza. La [guía oficial de Oculus](https://developers.meta.com/vr/blog/unlocking-oculus-go/) describe el cambio de política sobre `boot.img` y dm-verity; la [referencia de Qualcomm](https://www.qualcomm.com/news/onq/2017/01/secure-boot-and-image-authentication-mobile-tech) explica por qué eso no equivale a cambiar la autenticación que empieza en ROM.

## 1. Reproducir el análisis sin un visor

Desde la raíz del repositorio, inspecciona la muestra histórica depurada, compárala con un control sintético y ejecuta las pruebas:

```text
python tools/boot_state.py inspect examples/pacific-observed.txt
python tools/boot_state.py compare examples/pacific-locked-synthetic.txt examples/pacific-observed.txt
python -m unittest discover -s tests -v
```

El programa lee archivos locales y devuelve JSON; no consulta al visor. La marca `# evidence:` de una muestra es una etiqueta de origen, no una verificación independiente. La [observación histórica](SECURE_BOOT_FINDINGS.md#observación-histórica-en-un-visor) es de una unidad `pacific` el 25 de octubre de 2026. El control sintético simula un caso bloqueado: sólo comprueba el programa y no representa el estado anterior de esa unidad. Las diferencias entre las dos muestras son contrastes, no transiciones observadas. Ninguna dice en qué estado está el visor hoy.

| Entrada para el análisis | Comprobación esperada |
| --- | --- |
| `Secure boot: true` junto con `Device unlocked: true` | El análisis conserva ambos valores. El desbloqueo no convierte el otro campo en `false`. |
| Control sintético: falta `Secure boot` | Se informa que falta evidencia; no se toma el valor ausente como `false`. |
| Control sintético: el mismo campo aparece con dos valores incompatibles | La entrada es ambigua. No se conserva arbitrariamente el último valor. |
| Control sintético: se informa `Secure boot: false` | El texto representa lo que una fuente afirma, no una lectura de fusibles ni una prueba de desactivación. |

La primera fila reproduce una coexistencia observada. Los controles negativos detectan inferencias indebidas; no son resultados de hardware ni requieren cambiar el estado de una unidad.

## 2. Comparar observaciones ya existentes

Si tienes dos capturas independientes de una misma unidad, registra en privado la fecha, el producto y la versión de firmware reportada, si se conoce. Compara `Secure boot`, `Device unlocked`, `Device critical unlocked`, `Verified boot enabled` y `Verity enabled` **campo por campo**. Los cambios en uno no implican cambios en el resto. Si no tienes una captura anterior al desbloqueo, no fabriques una línea base ni interpretes una entrada sintética como si lo fuera. No es necesario volver a bloquear o desbloquear el visor para completar este análisis.

Si las capturas pertenecen a unidades o versiones distintas, trátalas como observaciones separadas: una diferencia no demuestra qué operación la provocó. Si una consulta falla, una etiqueta cambia de nombre o las fuentes se contradicen, conserva la incertidumbre y revisa las fuentes antes de sacar una conclusión.

## 3. Captura opcional de sólo lectura

Si el propietario está presente y el **Oculus Go ya está en Fastboot**, `fastboot devices` permite identificarlo. Usa el identificador únicamente en tu terminal local para acotar estas consultas al equipo correcto:

```text
fastboot -s SERIAL_LOCAL getvar product
fastboot -s SERIAL_LOCAL getvar secure
fastboot -s SERIAL_LOCAL oem device-info
```

Si `product` no es `pacific`, aparecen resultados contradictorios o no puedes confirmar la unidad, detente. Algunas respuestas pueden aparecer en stderr aun si la consulta se completó; revisa también el código de salida. Conserva cualquier captura bruta sólo en privado y comparte únicamente los campos anteriores, sin números de serie, rutas locales ni otros identificadores. No se ejecutaron estas consultas para preparar este documento.

El resultado del experimento es un conjunto de **indicadores reportados por el bootloader**, no una certificación independiente de la raíz de confianza. No avala que una imagen personalizada arranque, que una etapa concreta haya ejecutado código ni que un mecanismo de protección esté desactivado en el hardware.
