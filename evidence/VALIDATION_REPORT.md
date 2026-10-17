# Informe de ejecución final — SAT Arequipa 2.0.0

Fecha del cliente: 17 de octubre de 2026. Autor: Jordy Rolando Tejada Lazo.

## Herramientas y condiciones

VDMJ4.7.0 build260414, distribución oficial `4.7.0-release-fix`, publicada 14-04-2026.
Java18.0.1 (JDK directo), Windows, dialecto VDM++ / release VDM-10, gramática strict, UTF-8.
Precondiciones, postcondiciones, invariantes y comprobaciones dinámicas de tipos permanecieron
activadas; no se usaron las opciones de desactivación `-pre`, `-post`, `-inv` o `-dtc`.

## Resultados observados

- Seis clases: cinco de producción y TestSAT. Cero errores sintácticos, de tipos o inicialización;
  cero advertencias en la comprobación final.
- T01–T40: 40/40 retornaron `true`, código de salida0.
- N01–N08: 8/8 rechazaron la operación por precondición, como se esperaba.
- N09: rechazó construir Configuracion con umbrales iguales mediante invariante de tipo,
  como se esperaba. Los nueve casos negativos terminaron con código de salida1 esperado.
- Total: 49/49 resultados conformes al oráculo. No se contabilizan los nueve rechazos como
  pruebas normales que retornan `true`.
- Datos sintéticos, no lecturas de sensores ni resultados de campo.

`results.json` conserva caso, propósito, expresión, esperado, observado, código de salida,
veredicto, versión de herramientas, comandos, hashes SHA256 y ruta de cada log íntegro.

## Cobertura nativa de VDMJ

Después de repetir T01–T40 en una única sesión fresca se ejecutó `coverage <archivo>`:

| Fuente | Líneas cubiertas/ejecutables | Porcentaje nativo |
|---|---:|---:|
| Alarma.vdmpp |38/38|100,0% |
| Quebrada.vdmpp |33/33|100,0% |
| Sensor.vdmpp |14/14|100,0% |
| Sistema.vdmpp |127/128|99,2% |
| TiposSAT.vdmpp |21/21|100,0% |
| TestSAT.vdmpp |216/228|94,7% |

Son porcentajes de líneas ejecutables del reporte nativo del intérprete, no de expresiones ni
de todas las ramas, estados,
condiciones o requisitos. TestSAT incluye N01–N09, excluidos deliberadamente de esta sesión
de cobertura porque son rechazos esperados; sus ejecuciones independientes están registradas.
El reporte anotado completo y su resumen están en `coverage_execution.log` y `coverage.json`.
`*.cov` conserva sólo ubicaciones con hits; contar sus filas como denominador produciría
un falso100%. Se detectó y corrigió esa interpretación antes del cierre. Use
`../model/measure_coverage.ps1` para reproducir el porcentaje nativo.

## Obligaciones de prueba

VDMJ generó 80 obligaciones sobre las cinco clases de producción, sin errores del generador.
La salida final contiene 27 en estado Unproved y53 Unchecked; ninguna fue descargada.
La salida incorpora limitaciones del generador para contratos OO de VDM++, que no se ocultan.
Las pruebas y comprobaciones dinámicas no sustituyen la descarga deductiva de obligaciones.
No se afirma demostración universal, model checking exhaustivo o certificación de seguridad.

## Demostración ejecutada

`demo.log` y `demo_commands.txt` conservan operaciones reales del intérprete:

| Paso | Entrada/acción | Nivel, calidad, candidato | Versión |
|---|---|---|---:|
|1|Inventario con un sensor; reloj100; sin muestras|Verde, SinDatos, nil|4|
|2|Lectura1: humedad80%, inclinación4°, instante99|Rojo, Vigente, Rojo|5|
|3|Lectura2: humedad40%, inclinación3°, instante100|Rojo, Vigente, Verde|6|
|4|Registrar confirmación sobre lectura2|Rojo, Vigente, Verde; autorización objetivoVerde/v6|6|
|5|Aplicar descenso autorizado|Verde, Vigente, Verde; autorización consumida|7|

Paso2 creó un episodio con dos obligaciones Pendiente. Paso5 cerró el episodio sin borrar
esas dos obligaciones. Ni una clasificación sintética ni un intento lógico de aviso representan
predicción geotécnica, entrega SMS/correo o actuación real de una autoridad.

## Fallos encontrados y correcciones

La suite final no representa ausencia de defectos durante el desarrollo:

1. El primer alta de sensor violaba una invariante cruzada porque VDMJ revisa invariantes
   durante actualizaciones. Se corrigió creando una copia del snapshot de Quebrada y
   realizando commit `atomic` de sensores, asignación y quebradas; no se suspendieron checks.
2. `mk_token(mk_(<Episodio>,siguiente))` conservaba en VDMJ una referencia al contador mutable,
   lo que alteraba la clave del mapa al incrementarlo. Se materializó `siguiente+0` antes de
   construir el token. Las entradas también requieren IDs inmutables estables.
3. La auditoría amplió Evento para incluir snapshot de configuración/candidato y contexto
   explícito de alerta, autoridad y estado del aviso, evitando una trazabilidad sólo nominal.
4. Se corrigió el cálculo inicial de cobertura basado en `.cov`, sustituyéndolo por el reporte
   nativo de VDMJ. No se publica el porcentaje incorrecto inicial.

Las reproducciones independientes de los dos primeros fallos y las reejecuciones de auditoría
se conservan en `../review/` cuando se incluye dicha carpeta en el paquete de entrega.

## Límites de la conclusión

La evidencia apoya la conformidad de los escenarios ejecutados con los contratos y oráculos
bajo los supuestos del modelo. No prueba todas las ejecuciones posibles. Inventario aditivo,
reintentos manuales con incidencia ilustrativa al tercer intento, reloj abstracto, entradas pareadas,
operaciones externas secuenciales y canales de acuse de confianza son límites explícitos.
Retirada/traslado de sensores, persistencia, rendimiento, concurrencia, autenticación de red,
hardware y calibración geotécnica quedan fuera de esta versión final académica.
