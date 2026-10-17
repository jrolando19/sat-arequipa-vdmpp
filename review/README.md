# Revisión independiente del SAT Arequipa

Este directorio complementa la suite principal `model/TestSAT.vdmpp`. No modifica las clases de producción. La evidencia final corresponde a la versión congelada 2.0.0.

## Resultado y archivos principales

- `AuditSAT.vdmpp`: 24 verificaciones independientes; una recorre una grilla de 36 combinaciones de fronteras.
- `execution_final/positive_suite.log`: ejecución final, 24 valores `true`, cero errores y advertencias.
- `execution_final/audit_results.json`: comando, huellas SHA-256 y claves de las verificaciones.
- `final_review_summary.json`: contraste de las 49 salidas principales, las 24 verificaciones independientes, huellas concordantes, cobertura nativa por líneas y obligaciones abiertas.
- `quality_report.md`: hallazgos corregidos, límites y conclusiones admisibles para artículo y feria.

## Reproducción portable

Se necesita Python 3, Java compatible y el JAR de VDMJ 4.7.0. No se incluye ni instala Java desde este directorio. El paquete puede distribuirse sin runtimes. `model/bootstrap.ps1` recupera la distribución fijada y comprueba sus huellas, o se puede proporcionar el JAR manualmente.

Desde la raíz del paquete, cuya estructura es `model/`, `evidence/` y `review/`:

```powershell
python review/run_independent_audit.py execution_repro --java 'C:/ruta/jdk/bin/java.exe' --jar 'C:/ruta/vdmj-4.7.0.jar'
```

El primer argumento es una carpeta de salida opcional relativa a `review/`; esta copia pública usa por defecto `execution_reproduced`, excluida de la publicación. `--java` y `--jar` permiten indicar rutas de otro equipo. Java se busca en PATH salvo que se indique su ejecutable. Las nuevas ejecuciones no reemplazan `execution_final/`.

El runner mantiene las comprobaciones dinámicas activadas. No añadir `-pre`, `-post`, `-inv` ni `-dtc`: en VDMJ esas opciones las **desactivan**. El SHA-256 del JAR utilizado para la evidencia es:

`f57eb06f0116e76916b789f683345398b0c95a1bd860fdc176cd119f2b89b19d`

Para volver a contrastar las salidas finales de la suite principal, las huellas y la cobertura guardadas, sin ejecutar ni modificar el modelo:

```powershell
python review/verify_final_evidence.py
```

Ese segundo programa lee `evidence/results.json` y los logs, por lo que presupone que la suite principal fue ejecutada y que sus archivos acompañan al paquete. No debe confundirse esa comprobación documental con una nueva ejecución de los 49 casos.

## Diagnóstico separado: payload mutable de token

Los IDs de la frontera deben ser estables y construidos desde valores inmutables o materializados. En VDMJ no se debe encapsular directamente una estructura que conserva referencias a un contador mutable: se materializa el número, por ejemplo `contador+0`, antes de crear el token. El modelo materializa el contador de sus episodios; sus pruebas usan IDs estables.

`TokenBoundaryAudit.vdmpp` reproduce intencionadamente la violación de ese supuesto por un llamador externo. El resultado esperado es Error 4061 por cambio del hash de una clave. Es un diagnóstico conocido del uso de la herramienta, no uno de los 24 escenarios positivos, y no se cuenta como un caso del modelo aprobado.

```powershell
python review/run_independent_audit.py execution_repro --java 'C:/ruta/jdk/bin/java.exe' --jar 'C:/ruta/vdmj-4.7.0.jar' --include-boundary-diagnostic
```

Se guardan `token_boundary_diagnostic.log` y `token_boundary_diagnostic.json` aparte de `positive_suite.log`. La evidencia final conserva ambos resultados y declara explícitamente el supuesto de identidad estable.

## Lectura correcta de los resultados

Esta es una copia pública con rutas privadas redactadas. Los resultados y fuentes del modelo
se conservan; los logs públicos tienen hashes distintos de los originales privados por esa
redacción. Los logs intermedios de desarrollo y las revisiones de maquetación se conservan en
el archivo privado del proyecto, no se incluyen en este paquete público mínimo. Véanse el
README principal y `publication_manifest.json`.

Las 49 ejecuciones principales se desglosan en 40 comportamientos que retornan `true` y 9 rechazos deliberados de contrato. La auditoría adicional informa 24 verificaciones positivas por separado. No son 73 escenarios disjuntos del dominio: varias verificaciones contrastan de forma independiente propiedades ya ejercitadas en la suite principal.

La cobertura nativa de VDMJ se refiere aquí a **líneas ejecutables de fuente** de los 40 casos de comportamiento. No mide ramas, requisitos, estados ni pruebas exhaustivas. Los `.cov` exportados por defecto sólo guardan ubicaciones con hits y no aportan por sí solos el denominador. Las 80 obligaciones de prueba siguen sin descargarse (53 Unchecked y 27 Unproved).

El modelo es secuencial, usa datos sintéticos y no demuestra predicción de huaicos, calibración local, transporte de mensajes, autenticación real ni aptitud para activar una emergencia.
