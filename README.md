# SAT Arequipa — Especificación y validación en VDM++

**Autor:** Jordy Rolando Tejada Lazo · Ingeniería de Sistemas · Universidad Nacional de San Agustín de Arequipa.

Sistema de Alerta Temprana de Huaicos y Deslizamientos en Quebradas de Arequipa. Modelo académico **2.0.0**, sin cambios respecto de las fuentes congeladas que sustentan el artículo. Esta copia se preparó para publicación; este archivo no acredita que un repositorio ya haya sido publicado.

## Alcance y resultados

El núcleo recibe observaciones sintéticas de humedad e inclinación, evalúa umbrales por quebrada, conserva el nivel hasta un descenso autorizado y registra obligaciones de aviso por episodio y autoridad. No es un predictor geotécnico ni un sistema de emergencia desplegado.

| Evidencia ejecutada | Resultado |
|---|---:|
| Escenarios principales de comportamiento |40/40 retornan `true`|
| Rechazos deliberados de contrato |9/9 rechazos esperados|
| Verificaciones adicionales de auditoría |24/24 conformes|
| Obligaciones de prueba descargadas |0/80|

Las 24 verificaciones adicionales no son 24 escenarios del dominio disjuntos de los anteriores: contrastan también propiedades ya ejercitadas. Las 80 obligaciones permanecen abiertas: 27 `Unproved` y 53 `Unchecked`. Las pruebas finitas no demuestran corrección universal ni aptitud para uso operativo.

## Estructura

- `model/`: cinco clases de producción, `TestSAT.vdmpp` y scripts reproducibles.
- `evidence/`: copia pública redactada de resultados, logs, cobertura nativa, obligaciones y demostración.
- `review/`: `AuditSAT.vdmpp`, runner independiente y evidencia final; diagnóstico de identidad mutable separado.
- `figures/`: síntesis gráfica de evidencia para el artículo; no es una captura de una interfaz.
- `publication_manifest.json`: hashes originales/públicos, estado de preparación y diferencias declaradas.

## Reproducir

Se requiere Java compatible, PowerShell para la suite principal y Python3 para la auditoría adicional. La ejecución original usó Java18.0.1 y VDMJ4.7.0 build260414. No se incluyen runtimes ni se altera la instalación global de Java.

Desde la raíz del proyecto:

```powershell
./model/bootstrap.ps1
./model/validate.ps1 -JavaPath 'ruta/al/java.exe'
./model/demo.ps1 -JavaPath 'ruta/al/java.exe'
python review/run_independent_audit.py --java 'ruta/al/java.exe' --jar 'model/tools/vdmj-suite-4.7.0/vdmj-4.7.0.jar'
python review/verify_final_evidence.py
```

Los scripts públicos aceptan una ruta explícita de Java y, por defecto, buscan `java` en PATH. Las nuevas ejecuciones escriben en `evidence_reproduced/` o `review/execution_reproduced/`, no reemplazan la evidencia histórica y se excluyen de la publicación por `.gitignore`. Revise esas nuevas salidas antes de compartirlas: una ejecución local puede registrar rutas de su propio equipo.

`bootstrap.ps1` descarga una distribución oficial fijada y verifica SHA256 del ZIP y JAR. VDMJ tiene su propia licencia, disponible en esa distribución. No añada `-pre`, `-post`, `-inv` o `-dtc`: en VDMJ estas opciones **desactivan** las comprobaciones. El modelo se ejecutó con las cuatro activadas.

## Privacidad y fidelidad de esta copia

Las siete fuentes centrales —cinco clases de producción, `TestSAT.vdmpp` y `AuditSAT.vdmpp`— son **idénticas byte a byte** a las fuentes congeladas. Sus hashes originales y públicos coinciden.

En logs y metadatos históricos se sustituyeron rutas privadas absolutas por `<PROJECT_ROOT>`. Ese marcador es explicativo: para reconstruir un comando histórico debe sustituirse por la raíz local de este proyecto. Se preservaron las versiones, resultados, mensajes de error esperados, comandos lógicos y hashes originales de las fuentes.

Los hashes de archivos de evidencia cambian cuando se redacta una ruta o se recalcula el contraste de logs. `publication_manifest.json` relaciona ambas versiones. En `evidence/freeze.json`, `original_evidence_sha256_before_path_redaction` describe los originales privados, **no** los logs públicos. La publicación incluye versiones portables de runners; sus diferencias no alteran las fuentes VDM ni cuentan como una nueva versión del modelo.

Los documentos originales y la evidencia privada no se han modificado. No se incluyen credenciales, runtimes, perfiles personales ni datos de sensores reales. Los IDs `token` de las pruebas son identidades sintéticas del modelo, no credenciales de acceso.

## Límites principales

Inventario aditivo; reloj lógico; operaciones externas secuenciales; reintentos manuales con incidencia ilustrativa al tercer intento; umbrales sintéticos no geotécnicos; canales de acuse abstractos de confianza. Sin hardware, SMS/correo real, autenticación criptográfica, calibración local, persistencia ante reinicios ni estudio de rendimiento. Los IDs de entrada deben ser estables e inmutables; el diagnóstico separado documenta el uso incorrecto de payload mutable en VDMJ.

La cobertura nativa es por **líneas ejecutables**, no por ramas ni estados. Sistema cubre 127/128 líneas (99,2%); las demás clases de producción cubren todas sus líneas ejecutables en esos escenarios. Esta métrica no reemplaza requisitos, revisión ni obligaciones de prueba.
