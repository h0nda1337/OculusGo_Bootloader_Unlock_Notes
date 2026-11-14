# Oculus Go: bootloader y Secure Boot

Notas independientes sobre el desbloqueo que Oculus publicó para el **Oculus Go**. Desbloquear el bootloader no equivale a desactivar Secure Boot ni a romper la cadena de confianza del SoC. Este repositorio no contiene software de desbloqueo, imágenes de firmware ni métodos para eludir la verificación de la cadena de arranque.

**Resultado de la revisión:** no encontramos un método público, oficial o soportado para desactivar Secure Boot del SoC en el Oculus Go (`pacific`). El paquete oficial sí cambia la política de arranque de Android. Consulta [las fuentes, la observación del visor y los límites de la conclusión](SECURE_BOOT_FINDINGS.md).

## Qué cambia con el método oficial

La [guía de Oculus](https://developers.meta.com/vr/blog/unlocking-oculus-go/) explica que, una vez desbloqueado el bootloader, éste deja de exigir una firma de Oculus en `boot.img` y de imponer dm-verity mediante la línea de comandos del kernel. Eso describe la política del bootloader para Android; no demuestra que los componentes anteriores de arranque puedan sustituirse ni que el desbloqueo crítico esté habilitado.

En Fastboot, `Secure boot: true`, `Device unlocked: true` y `Device critical unlocked: false` pueden coexistir. Son indicadores distintos. Tampoco prueban que una imagen concreta sea compatible o que haya ejecutado código en el visor.

## Antes de usar el paquete

- Usa únicamente el [paquete oficial Oculus Go SW Unlock](https://developers.meta.com/vr/downloads/package/oculus-go-sw-unlock/) para ese modelo. Consulta la guía de Oculus para el procedimiento; este repositorio no incluye copias del paquete.
- Haz copia de tus datos. Oculus advierte que el desbloqueo borra los datos del dispositivo y que instalar el sistema desbloqueable interrumpe las actualizaciones OTA. Volver a bloquear el bootloader no revierte la instalación; además, vuelve a borrar los datos y, con una imagen de arranque no firmada, el dispositivo podría no iniciar.
- Consulta los [términos y advertencias oficiales](https://developers.meta.com/vr/licenses/go-unlock-tos/). El paquete no es para otros visores.

## Comprobar el estado sin cambiarlo

Si el visor ya está en Fastboot, `fastboot devices` comprueba que el PC lo detecta. En el Oculus Go, `fastboot -s <serial-local> oem device-info` consulta los indicadores anteriores. Sustituye `<serial-local>` por el identificador de tu visor; ocúltalo antes de compartir resultados, porque puede aparecer también en la salida del segundo comando. Ninguna consulta prueba el arranque de una imagen.
