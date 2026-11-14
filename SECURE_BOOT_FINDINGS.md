# ¿Se puede desactivar Secure Boot oficialmente en el Oculus Go?

**Revisión: 13 de noviembre de 2026. No encontramos un método público, oficial o soportado para desactivar la cadena de arranque seguro del SoC en el Oculus Go (`pacific`).** Meta sí publica un desbloqueo del bootloader. La conclusión se limita a las fuentes consultadas: no afirma que la desactivación sea imposible ni descarta documentación no pública.

## Qué verifican las fuentes

| Capa | Hallazgo |
| --- | --- |
| Secure Boot del SoC | [Qualcomm describe](https://www.qualcomm.com/news/onq/2017/01/secure-boot-and-image-authentication-mobile-tech) una cadena de autenticación que empieza en ROM. Es una referencia de arquitectura general, no una descripción de los fusibles ni de todas las etapas del Go. |
| Firma de `boot.img` | La [guía oficial de Oculus, del 21 de octubre de 2021](https://developers.meta.com/vr/blog/unlocking-oculus-go/), indica que el bootloader desbloqueado deja de exigir la firma de Oculus en `boot.img`. Es una política posterior a las primeras etapas de arranque. |
| dm-verity de Android | La misma guía indica que el bootloader deja de imponer dm-verity mediante la línea de comandos del kernel. [AOSP documenta](https://source.android.com/docs/security/features/verifiedboot/dm-verity#operation) que dm-verity comprueba la integridad de dispositivos de bloques desde el kernel, no desde la ROM inicial. |
| Secure Boot de UEFI | La [especificación UEFI](https://uefi.org/specs/UEFI/2.11/32_Secure_Boot_and_Driver_Signing.html) describe una política para autenticar imágenes UEFI. Que un firmware experimental la implemente o no es independiente de la verificación anterior al arranque de ese firmware. |

Revisamos la guía, la [ficha del paquete oficial 1.0, fechada el 18 de octubre de 2021](https://developers.meta.com/vr/downloads/package/oculus-go-sw-unlock/) y los [avisos del proveedor](https://developers.meta.com/vr/licenses/go-unlock-tos/). El paquete se describe como acceso de bajo nivel exclusivo de este visor. La guía habla de `boot.img`, dm-verity y acceso root; ninguna de ellas documenta desactivar la raíz de confianza del SoC. Una búsqueda en documentación pública de Meta/Oculus con el nombre del modelo y términos como `Secure Boot`, `disable` y `bootloader unlock` no encontró un procedimiento adicional para ese fin. No inspeccionamos ni redistribuimos el ZIP.

## Observación histórica en un visor

El 25 de octubre de 2026, una consulta de sólo lectura a un Go que ya tenía el desbloqueo oficial instalado devolvió `pacific` en `fastboot getvar product` y `secure: yes` en `fastboot getvar secure`. De `fastboot oem device-info` se conservan aquí sólo estos campos, sin número de serie ni salida sin filtrar:

```text
Secure boot: true
Verity enabled: false
Verified boot enabled: false
Device unlocked: true
Device critical unlocked: false
```

Estos valores fueron reportados por el bootloader de **una unidad**, no medidos directamente en hardware. Demuestran que, en esa observación, el indicador de Secure Boot seguía activo mientras el bootloader estaba desbloqueado. No atestiguan los fusibles, el estado de todas las etapas ni el arranque de una imagen personalizada. No se hizo una consulta nueva al visor para esta revisión.

Para un port de firmware, no hay evidencia de que desactivar la cadena del SoC sea un requisito para presentar una `boot.img` al bootloader desbloqueado. Tampoco hay garantía de que una imagen concreta arranque: que Fastboot acepte un comando no demuestra ejecución de código.
