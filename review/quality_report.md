# Informe independiente de calidad técnica

Proyecto: Sistema de Alerta Temprana de Huaicos y Deslizamientos en Quebradas de Arequipa. Autor del proyecto: Jordy Rolando Tejada Lazo. Revisión del 17/10/2026; entrega comunicada por el autor: 20/10/2026, sin hora indicada.

## Dictamen sobre la instantánea auditada

La especificación ejecutable revisada implementa el núcleo secuencial de recepción, clasificación conservadora, retención/descenso autorizado y outbox lógico por episodio y destinatario. La suite independiente devuelve **24 verificaciones verdaderas, ninguna falsa, cero errores de sintaxis/tipos y cero advertencias**, con las comprobaciones dinámicas de precondiciones, postcondiciones e invariantes activadas. Una de esas verificaciones recorre 36 combinaciones de fronteras de humedad e inclinación; son 24 verificaciones, no 59 pruebas distintas.

Esto respalda los escenarios concretos ejecutados. No es demostración universal, descarga de obligaciones de prueba, certificación de seguridad ni validación geotécnica. La evidencia final corresponde a las huellas SHA-256 registradas en `execution_final/audit_results.json`, sobre las fuentes congeladas 2.0.0. Se contrastó su igualdad con las huellas de la suite principal. Si cambia una fuente, debe repetirse la suite.

## Método y reproducción

- Entorno: Java 18.0.1 y VDMJ 4.7.0. Jar SHA-256: `f57eb06f0116e76916b789f683345398b0c95a1bd860fdc176cd119f2b89b19d`.
- `AuditSAT.vdmpp` es una clase de pruebas independiente de `TestSAT.vdmpp` y no modifica las cinco fuentes del modelo.
- Ejecutar `run_independent_audit.py <directorio_de_salida>` con Python. El programa utiliza la ruta directa del JDK, conserva salida completa y huellas de las fuentes y no usa `-pre`, `-post`, `-inv` ni `-dtc`. Esas opciones de VDMJ **desactivan** comprobaciones.
- Evidencia positiva final: `execution_final/positive_suite.log` y `execution_final/audit_results.json`. El runner admite argumentos portables `--java` y `--jar`; instrucciones completas en `README.md`.
- Datos sintéticos: humedad 0–100; inclinación 0–180; configuración 60/80 y 5/10, vigencia 30. No son umbrales operativos de Arequipa.

## Hallazgos concretos detectados y resueltos

| ID | Fallo observado | Corrección y verificación |
|---|---|---|
| H01 | `RegistrarSensor` actualizaba primero el mapa de sensores y dejaba temporalmente distintos los dominios de sensores/asignación y el inventario de la quebrada. VDMJ abortaba con Error 4130, `inv_Sistema`. | Se prepara un objeto Quebrada nuevo con el snapshot actualizado, fuera del agregado, y se confirma mediante asignación atómica de los tres mapas. No se relajó la invariante ni se desactivaron las comprobaciones. La suite posterior supera el alta y la ampliación de inventario. Evidencia del fallo: `execution_01/positive_suite.log`. |
| H02 | Al abrir el episodio, el token encapsulaba una tupla con la referencia mutable `siguiente`. Tras incrementar el contador, la clave quedaba inaccesible en el mapa; Error 4061 en `inv_Alarma`, clave observada con número 2. | Se materializa el número (`siguiente+0`) antes de encapsularlo. La suite verifica primer Rojo, reintentos y segundo episodio tras descenso. Evidencia del fallo: `execution_02/positive_suite.log`. Se describe como defecto observado de la realización/interacción con el intérprete, no como una propiedad general de todos los `token` en VDM++. |
| H03 | La auditoría inicial no conservaba configuración/candidato de decisiones antiguas y faltaban eventos de tiempo, confirmación, envío y acuse. | Se incorporó snapshot completo de Evaluacion a Evento y eventos de esas operaciones, con contexto alerta/autoridad/Aviso en comunicaciones. A19 comprueba que la configuración histórica y el candidato previo permanecen intactos tras un cambio; A31 conserva el contexto y snapshot Enviada aun después del acuse. |
| H04 | Un llamador externo construye el ID encapsulando una tupla que contiene un contador mutable, registra el ID y luego cambia el contador; en VDMJ la clave puede cambiar de hash y producir Error 4061. | Limitación residual del uso de la herramienta y supuesto explícito de frontera: IDs estables construidos desde valores inmutables/materializados. El modelo materializa sus propios contadores; no puede inspeccionar el payload opaco de un token arbitrario entrante. Reproducción y salida separadas en `TokenBoundaryAudit.vdmpp` y `execution_final/token_boundary_diagnostic.log`. No pertenece a los 24 casos positivos ni se cuenta como aprobado. |

## Correspondencia de comprobaciones independientes

| Área | RF/RFD | Verificaciones ejecutadas |
|---|---|---|
| Identidad y frontera | RF1, RFD1–2 | A01 sensor desconocido; A02 origen cruzado; A03 incompleta; A04 rango, degradación y recuperación; A06 ID/número duplicado; A07 tiempo futuro/negativo. |
| Vigencia y ausencia | RF1–RF2, RFD3 | A08 frontera inclusiva 30/31; A09 SinDatos/nil; A10 cobertura parcial crítica. |
| Clasificación y agregación | RF2, RFD5 | A12 grilla 6×6; A14 máximo entre sensores. |
| Retención y confirmación | RF2, RFD6 | A17 lectura nueva invalida autorización sin avance del reloj entre ambas; A18 caducidad; A20 descenso válido, consumo y cierre; A22 cambio de configuración sin descenso automático; A28 alta invalida y reduce cobertura; A30 actividad de otra quebrada conserva confirmación. |
| Episodios y avisos | RF3, RFD7–8 | A23 acuse independiente y no regresión de Confirmada; A24 tres fallos conservan clave y generan incidencia; A25 segundo episodio conserva avisos anteriores. |
| Aislamiento y encapsulación | RF1–RF3 | A27 estado de q2 intacto ante recepción/configuración de q1; A29 modificación de snapshot del llamador no cambia el agregado. |
| Auditoría histórica | RFD9 | A19 snapshot anterior de configuración/candidato no se reescribe al cambiar parámetros; A31 contexto alerta/autoridad/Aviso conserva estado anterior al acuse. |

Las pruebas positivas por sí solas no comprueban que todos los contratos rechacen cualquier entrada inválida. Las pruebas negativas de la suite principal se deben informar por separado con el error esperado y el contexto de la operación; no llamar ‘fallos del proyecto’ a rechazos deliberados conformes al contrato.

## Límites y coherencia documental obligatorios

1. **Inventario aditivo.** Esta versión registra sensores, pero no implementa bajas, traslados ni desactivaciones. T24 cubre alta e invalidación de confirmación, no alta/baja como decía el plan inicial. Las propuestas anteriores de retiro y catálogo histórico no deben afirmarse como implementadas.
2. **Quebrada vacía.** Puede existir antes de registrar sensores; permanece SinDatos y sin candidato. No hay operación/estado explícito de ‘habilitación’. No afirmar que toda quebrada registrada tiene un sensor: sí tiene destinatarios no vacíos.
3. **Reintentos manuales.** El modelo registra intentos y una incidencia a partir de tres. No bloquea los posteriores, no programa un intervalo ni garantiza entrega eventual. No afirmar scheduler, límite duro o parámetros operativos configurables si no se añaden.
4. **Confirmación conservadora.** Cada evaluación ordinaria invalida confirmaciones; el avance del reloj las invalida incluso si las muestras aún no vencen. Es más estricto que invalidar sólo al caducar. La configuración exige versión exactamente anterior+1.
5. **Auditoría lógica, no física.** Los eventos conservan snapshot de evaluación y, para comunicaciones, episodio/autoridad/aviso. Esto permite revisar la secuencia abstracta; no es un registro resistente a manipulación, evidencia criptográfica ni prueba de tránsito por una red real.
6. **Autoridad y autenticidad abstractas.** La comparación con un token de operador y la recepción de una clave de acuse son supuestos lógicos, no mecanismos de autenticación, firmas ni evidencia de recepción física. Enviada no equivale a recibida/atendida. El modelo admite acuse sobre una obligación pendiente como evento externo; no exige intento interno previo.
7. **Retención, no banda física de histéresis.** No se implementan umbrales descendentes distintos. Se conserva el nivel hasta una confirmación válida. Usar ese término preciso evita confundir el mecanismo con calibración física.
8. **Secuencialidad.** La coordinación se interpreta como transición secuencial/atómica bajo el supuesto del modelo. No se ha verificado concurrencia, red distribuida, caída durante escritura ni durabilidad de base de datos.
9. **Escalabilidad estructural.** Se prueban múltiples sensores y quebradas y separación por identidad; no se midió rendimiento, volumen máximo ni latencia.
10. **Sin validación de campo.** No hay sensores instalados, umbrales locales calibrados, corpus de eventos, sensibilidad, especificidad ni tasa de falsas alarmas. El proyecto no decide evacuaciones reales.
11. **Identidades estables en la frontera.** No encapsular una referencia mutable compartida dentro de un token. Usar literales inmutables o materializar el valor (por ejemplo, `contador+0`). La revisión de snapshots positivos no justifica afirmar inmunidad absoluta frente a payloads mutables introducidos por código externo.

## Contraste final de evidencia principal, cobertura y obligaciones

`verify_final_evidence.py` contrastó los 49 logs principales con los resultados declarados: 40 retornos verdaderos y 9 rechazos de contrato esperados (8 precondiciones y 1 invariante). Sus fuentes de producción coinciden con las cinco huellas de la ejecución independiente final. Las 24 comprobaciones independientes son adicionales, pero no se presentan como escenarios disjuntos de los 49.

Se detectó y corrigió una interpretación errónea inicial de la cobertura: la exportación `.cov` predeterminada de VDMJ sólo escribe ubicaciones con hits. Contar sus filas como numerador y denominador produce un 100 % tautológico. Se contrastó el bytecode del JAR fijado (`SourceFile.writeCoverage` delega con `false`) y se verificó el informe nativo `coverage`, cuyo denominador son líneas ejecutables. El archivo final `evidence/coverage_execution.log` contiene el detalle completo de líneas cubiertas/no cubiertas para los 40 comportamientos, excluyendo los casos negativos.

| Fuente | Líneas cubiertas / ejecutables | Porcentaje nativo |
|---|---:|---:|
| Alarma | 38 / 38 | 100,0 % |
| Quebrada | 33 / 33 | 100,0 % |
| Sensor | 14 / 14 | 100,0 % |
| Sistema | 127 / 128 | 99,2 % |
| TiposSAT | 21 / 21 | 100,0 % |
| TestSAT | 216 / 228 | 94,7 % |

Los porcentajes se truncan a un decimal en el reporte nativo. No son cobertura de expresiones, ramas, estados o requisitos. La fuente de prueba se presenta separada de producción y no se promedian porcentajes con denominadores diferentes.

Se verificaron 80 obligaciones generadas: **53 Unchecked y 27 Unproved; ninguna descargada por este trabajo**. Las marcas Unchecked incluyen límites del generador para VDM++/RT; no equivalen a teoremas aprobados. El proyecto informa validación ejecutable acotada, no demostración deductiva.

## Formulaciones aptas para artículo/feria

- Adecuado: ‘El modelo fue ejecutado con contratos e invariantes dinámicos activos y satisfizo los escenarios sintéticos reportados’.
- Adecuado: ‘La política conservadora permite escalar con cobertura parcial, pero exige cobertura completa y autorización vigente para descender’.
- Adecuado: ‘El outbox lógico mantiene obligaciones independientes por episodio y destinatario; la entrega física queda fuera del modelo’.
- Inadecuado: ‘Se demostró que nunca falla’, ‘se garantiza detectar huaicos’, ‘el sistema es seguro para uso real’, ‘se probaron todos los estados’ o ‘las autoridades reciben el aviso en tiempo real’.

## Cierre de esta revisión

La auditoría se repitió sobre las fuentes congeladas; la suite principal, su cobertura nativa y los estados de obligaciones se contrastaron sin modificar las fuentes. `final_review_summary.json` conserva cantidades, claves, huellas y rutas de cada log. No queda un fallo bloqueante dentro del alcance condicionado por identidades estables; los límites anteriores deben mantenerse en los documentos. La preparación de video y diapositivas es un entregable adicional al documento técnico y al artículo, aunque este informe no los produce.
