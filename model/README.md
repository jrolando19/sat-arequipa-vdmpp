# SAT Arequipa — especificación formal VDM++ 2.0.0

Autor: Jordy Rolando Tejada Lazo. UNSA, Aspectos Formales de Especificación y Verificación.
Entrega académica: martes 20 de octubre de 2026. No es un sistema geotécnico certificado.

## Contenido

- `TiposSAT.vdmpp`: tipos quote/token, registros, invariantes de tipo y funciones puras.
- `Sensor.vdmpp`: identidad, última lectura aceptada y degradación explícita.
- `Quebrada.vdmpp`: estado por quebrada, configuración y confirmación consumible.
- `Alarma.vdmpp`: episodios y outbox por `(IdAlerta, IdAutoridad)`.
- `Sistema.vdmpp`: fachada; inventario, recepción, evaluación, reloj y trazabilidad.
- `TestSAT.vdmpp`: 40 escenarios de comportamiento y 9 rechazos de contrato esperados.
- `../evidence/`: salidas íntegras, resultados JSON, cobertura, obligaciones y demostración.
- `../review/`: revisión y ejecución independientes, si se distribuye junto al modelo.

## Reproducción en Windows/PowerShell

Se validó con Java18.0.1 y VDMJ4.7.0 build260414. No se modificó Java ni su configuración global.
La ruta Oracle `javapath` del equipo no respondió; se utilizó directamente el ejecutable del JDK.
En otro equipo, indique la ruta real de su Java compatible con VDMJ.

```powershell
./bootstrap.ps1
./validate.ps1 -JavaPath 'C:/ruta/al/jdk/bin/java.exe'
./demo.ps1 -JavaPath 'C:/ruta/al/jdk/bin/java.exe'
```

`bootstrap.ps1` descarga la distribución oficial fijada y comprueba SHA256 del ZIP y JAR.
`tools/` contiene dependencias de terceros: no forma parte de las fuentes propias.
El código puede distribuirse sin `tools/`; se recupera con el script anterior.
VDMJ tiene su propia licencia (`LICENCE` en la distribución).

VDMJ activa comprobaciones de precondición, postcondición, invariantes y tipos dinámicos por defecto.
**No** añadir `-pre`, `-post`, `-inv` ni `-dtc`: esas opciones las DESACTIVAN.
La sesión interactiva de cobertura y demo además las establece explícitamente en `on`.

Cada T01–T40 debe retornar `true` con código de salida0. N01–N08 deben producir un fallo de
precondición; N09 debe producir un fallo de invariante de Configuracion. Estos nueve rechazos
son resultados esperados y demuestran que los contratos no se ignoraron; no se cuentan como
pruebas normales que retornaron `true`.

## Política y unidades

Humedad: real en[0,100] por ciento normalizado. Inclinación: real en[0,180] grados respecto de
una referencia abstracta. Son convenciones del modelo, no límites de estabilidad de ladera.
Tiempo: nat en ticks lógicos, no segundos ni reloj de hardware. Edad <=TTL es vigente.
Entradas poseen magnitudes opcionales y enteros sin restringir para probar errores; sólo tras
validar se construye Lectura con su invariante. Número e instante deben crecer estrictamente
por sensor; IDs de lecturas aceptadas no se repiten globalmente.

Configuración didáctica: humedad aviso60/crítico80; inclinación aviso5/crítico10; TTL30ticks.
No son umbrales geotécnicos de Arequipa ni recomendaciones de uso real. Cada quebrada puede
tener otra configuración válida; su versión debe ser exactamente la anterior+1 al cambiarla.

Una magnitud crítica basta para Rojo; de lo contrario una en aviso basta para Amarillo.
El candidato es el máximo de las últimas muestras utilizables. Sin muestras es `nil`, no Verde.
Cobertura completa significa calidad Vigente; parcial, Degradada; ninguna, SinDatos.
La calidad no es un color de alerta. Verde inicial con SinDatos no significa seguridad confirmada.

La alerta se retiene o escala automáticamente. El descenso exige cobertura completa, candidato
inferior y confirmación del operador sobre una lectura actual y la versión exacta de la quebrada.
La autorización se consume. Nueva lectura aceptada, nuevo intento inválido degradante, cambio
de configuración, alta de sensor o reevaluación del reloj la invalida. Una llamada a AvanzarTiempo
recalcula todas las quebradas e invalida incluso si el tick no cambia: regla conservadora explícita.
Una nueva lectura de q2 no invalida la confirmación de q1. No hay banda numérica de histéresis;
la retención y el descenso autorizado constituyen la política anti-oscilación adoptada.

## Invariantes y contratos

Las invariantes de registro acotan lecturas y ordenan umbrales; Evaluacion liga calidad/candidato
y confirmación/versión. Sensor preserva el origen de su última lectura. Sistema preserva dominio
de mapas, asignación única, activos coherentes, referencias históricas y orden por sensor.
Alarma exige exactamente una clave por episodio y destinatario y no permite dos episodios
abiertos de la misma quebrada. La no reducción ordinaria es una **propiedad de transición**,
expresada en postcondiciones de Quebrada, no una invariante de un solo estado.

El alta de sensor usa una copia nueva del snapshot de Quebrada y un commit `atomic` de los tres
mapas. No se emplea un flag para suspender invariantes ni se desactivan sus comprobaciones.
La identidad del episodio materializa el contador (`siguiente+0`) antes de envolverlo en token;
así evita una clave basada en una referencia mutable del intérprete.

Evento conserva orden, instante, causa, quebrada y snapshot íntegro de Evaluacion, incluida
configuración/candidato/calidad/versión. En envío/acuse conserva además alerta, autoridad y
snapshot de Aviso; el descenso conserva el episodio que cierra. Intento conserva cada entrada,
resultado y ahora, también si el sensor es desconocido. Rechazar no reemplaza el historial válido.

## Avisos, escalabilidad y límites

Entrar a Rojo crea un episodio y una obligación Pendiente por autoridad configurada, dentro
de la misma operación externa de recepción/evaluación. Se supone ejecución secuencial sin
intercalado de operaciones externas; no se modela concurrencia distribuida ni fallos del proceso.
Enviada significa sólo intento lógico de emisión. Un acuse se recibe como evento abstracto de un
canal de confianza; no se implementa autenticación criptográfica del entorno.

Reintentos son manuales, sin temporizador ni planificación. Tres intentos no confirmados marcan
incidencia, pero no borran la obligación ni prohíben posteriores intentos. El valor3 es ilustrativo.
Un aviso confirmado no vuelve a enviarse; un acuse es idempotente y sólo afecta a su destinatario.
Cerrar episodio no borra avisos; otro retorno a Rojo crea otra identidad.

Inventario aditivo: se dan de alta varias quebradas y sensores, pero no se retiran ni trasladan.
Una quebrada vacía está registrada pero no habilitada para evaluar seguridad (SinDatos/nil).
La escala se expresa en mapas y separación por quebrada, no en rendimiento medido. Historiales
no están acotados; retención persistente, rendimiento y adaptación a almacenamiento quedan
fuera de esta versión. No se ejecutan sensores físicos, SMS, simulación geotécnica ni predicción.

La cobertura es de líneas ejecutables del reporte nativo de VDMJ por fuente, no de expresiones,
requisitos ni de
todas las ramas/estados. Los ficheros `.cov` sólo guardan hits; no se usa su número de filas como
denominador. Las 80 obligaciones generadas quedan sin descargar (27Unproved y53Unchecked): no se afirma prueba
deductiva universal, descarga de teoremas, model checking exhaustivo ni certificación de seguridad.

Los IDs del entorno deben ser valores estables. En VDMJ no debe construirse un token directamente
desde un contador o estructura mutable compartida: use un literal inmutable o materialice el
valor (`contador+0`) antes de `mk_token`. El intérprete puede conservar una referencia mutable
en ese payload, cambiando su hash tras la mutación; la auditoría independiente reprodujo esta
limitación. Las entradas y pruebas de este modelo usan IDs inmutables materializados.
