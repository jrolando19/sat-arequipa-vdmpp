param(
  [string]$JavaPath = 'java',
  [string]$JarPath = "$PSScriptRoot/tools/vdmj-suite-4.7.0/vdmj-4.7.0.jar",
  [string]$EvidenceDir = "$PSScriptRoot/../evidence_reproduced"
)
$ErrorActionPreference = 'Stop'
$sources = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.vdmpp' | Sort-Object Name | ForEach-Object FullName)
$evidence = [IO.Path]::GetFullPath($EvidenceDir)
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
$common = @('-jar', $JarPath, '-vdmpp', '-r', 'vdm10', '-strict', '-c', 'UTF-8')
# IMPORTANT: VDMJ -pre, -post, -inv and -dtc DISABLE checks. None is used.
$checks = @(& $JavaPath @common @sources 2>&1)
$checkExit = $LASTEXITCODE
$checks | Set-Content -LiteralPath "$evidence/typecheck.log" -Encoding utf8
if ($checkExit -ne 0 -or ($checks -join "`n") -notmatch 'No type errors') {
  throw "VDMJ typecheck failed. Read $evidence/typecheck.log"
}
$purposes = @(
  'Sensor desconocido: rechazo sin modificación',
  'Humedad negativa: última válida preservada y sensor degradado',
  'Inclinación 181: rechazo por rango',
  'Identidad duplicada: sin duplicar historial ni avisos',
  'Lectura atrasada/futura: rechazo y muestra anterior conservada',
  'Vigencia inclusiva edad30 y expiración31, conserva Rojo',
  'Clasificación Verde con cobertura completa',
  'Límites Amarillo: humedad60 e inclinación5',
  'Límites Rojo: humedad80 e inclinación10',
  'Verde a Rojo directo: episodio y dos obligaciones pendientes',
  'Predicado rechaza umbrales iguales o invertidos',
  'Inicio: SinDatos y candidato nil',
  'Lectura baja no reduce Rojo sin confirmación',
  'Lecturas contradictorias: máximo Rojo',
  'Nueva lectura invalida confirmación',
  'Caducidad invalida confirmación y conserva Rojo',
  'Descenso autorizado consume confirmación y conserva avisos',
  'Confirmación consumida queda ausente',
  'Configuración versionada invalida confirmación sin descenso',
  'Acuses independientes por autoridad',
  'Tres reintentos mantienen clave y generan incidencia',
  'Nuevo episodio tras descenso y retorno a Rojo',
  'Aislamiento de dos quebradas',
  'Alta aditiva de sensor: inventario consistente y confirmación invalidada',
  'Observación incompleta: rechazo sin lectura aceptada',
  'Extremos válidos (0,0) y (100,180)',
  'Origen de lectura incompatible: rechazo',
  'Cobertura parcial puede escalar pero informa Degradada',
  'Nueva lectura válida recupera calidad tras intento inválido',
  'Nueva lectura de q2 no invalida confirmación q1',
  'Acuse idempotente y aviso confirmado no se reintenta',
  'Nueva configuración más estricta escala y genera obligaciones',
  'Entrada ya caducada rechazada',
  'Número cero e instante negativo rechazados',
  'Igual instante con número mayor rechazado',
  'Secuencia de eventos con orden consecutivo',
  'Contexto explícito e inmutable de envío y acuse en eventos',
  'Descenso autorizado Rojo a Amarillo y Amarillo a Verde',
  'Configuración y candidato históricos preservados tras reconfigurar',
  'Reevaluación temporal conservadora invalida confirmación incluso en igual tick'
)
$negativePurposes = @(
  'Alta duplicada de sensor', 'Actor no autorizado', 'Retroceso del reloj',
  'Descenso sin confirmación', 'Reutilización de confirmación consumida',
  'Acuse sin obligación existente', 'Confirmación con candidato Rojo',
  'Configuración sin incremento de versión', 'Construcción de configuración inválida'
)
$results = @()
foreach ($n in 1..40) {
  $id = 'T{0:00}' -f $n
  $expression = "new TestSAT().$id()"
  $out = @(& $JavaPath @common '-e' $expression @sources 2>&1)
  $code = $LASTEXITCODE
  $out | Set-Content -LiteralPath "$evidence/$id.log" -Encoding utf8
  $joined = $out -join "`n"
  $pass = $code -eq 0 -and $joined -match '(?m)^true\s*$' -and $joined -notmatch 'Execution: Error'
  $results += [ordered]@{id=$id; purpose=$purposes[$n-1]; kind='behaviour'; expected='true';
    observed=if($pass){'true'}else{$joined}; exit_code=$code; verdict=if($pass){'PASS'}else{'FAIL'};
    expression=$expression; log="$id.log"}
  Write-Output "$id $(if($pass){'PASS'}else{'FAIL'})"
}
foreach ($n in 1..9) {
  $id = 'N{0:00}' -f $n
  $expression = "new TestSAT().$id()"
  $out = @(& $JavaPath @common '-e' $expression @sources 2>&1)
  $code = $LASTEXITCODE
  $out | Set-Content -LiteralPath "$evidence/$id.log" -Encoding utf8
  $joined = $out -join "`n"
  $expected = if($n -eq 9){'invariant violation'}else{'precondition violation'}
  $match = if($n -eq 9){'invariant violated|invariant violation'}else{'Precondition failure|precondition violated'}
  $pass = $code -ne 0 -and $joined -match $match -and $joined -match 'No type errors'
  $observed = @($out | Where-Object {$_ -match 'Execution: Error'}) -join ' '
  $results += [ordered]@{id=$id; purpose=$negativePurposes[$n-1]; kind='expected-contract-rejection';
    expected=$expected; observed=$observed; exit_code=$code; verdict=if($pass){'PASS'}else{'FAIL'};
    expression=$expression; log="$id.log"}
  Write-Output "$id $(if($pass){'PASS'}else{'FAIL'})"
}
$hashes = @($sources | ForEach-Object {Get-FileHash -Algorithm SHA256 -LiteralPath $_} |
  Select-Object @{Name='file';Expression={[IO.Path]::GetFileName($_.Path)}},Hash)
$version = @(& $JavaPath '-version' 2>&1) -join "`n"
$vdmjVersion = @(& $JavaPath '-jar' $JarPath '-v' 2>&1) -join "`n"
$summary = [ordered]@{
  model_version='2.0.0'; client_date='2026-10-17'; execution_utc=[DateTime]::UtcNow.ToString('o');
  language='VDM++ / VDM-10'; vdmj=$vdmjVersion; java=$version;
  source_url='https://github.com/nickbattle/vdmj/releases/tag/4.7.0-release-fix';
  jar_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $JarPath).Hash;
  checks=[ordered]@{preconditions=$true;postconditions=$true;invariants=$true;dynamic_types=$true};
  command_prefix=@($JavaPath)+$common; sources=$sources; source_hashes=$hashes;
  behavioural_cases=40; expected_negative_cases=9;
  total=$results.Count; passed=@($results|Where-Object {$_.verdict -eq 'PASS'}).Count;
  failed=@($results|Where-Object {$_.verdict -eq 'FAIL'}).Count; results=$results;
  limitations=@('Synthetic data; not geotechnical validation','No real SMS/email delivery',
    'Sequential atomic external operations; no distributed concurrency',
    'Additive inventory only; removal and relocation out of scope',
    'Manual logical retries; incidence threshold3 is illustrative, not a scheduler',
    'No theorem discharge or exhaustive model checking claimed')
}
$summary | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath "$evidence/results.json" -Encoding utf8
Write-Output "TOTAL $($summary.passed)/$($summary.total) PASS"
if($summary.failed -gt 0){exit 1}
# A single fresh interpreter collects line-expression coverage for the 40 behavioural cases.
# Coverage is NOT a proof, branch-coverage metric or exhaustive state exploration.
$coverageDir = Join-Path $evidence 'coverage'
New-Item -ItemType Directory -Force -Path $coverageDir | Out-Null
$coverageCommandPath = $coverageDir -replace '\\','/'
$commands = @('set pre on','set post on','set inv on','set dtc on') +
  @(1..40 | ForEach-Object {'print new TestSAT().T{0:00}()' -f $_}) +
  @("coverage write $coverageCommandPath") +
  @($sources | ForEach-Object {'coverage ' + ($_ -replace '\\','/')}) + @('quit')
$coverageOut = @($commands | & $JavaPath @common '-i' @sources 2>&1)
$coverageExit = $LASTEXITCODE
$coverageOut | Set-Content -LiteralPath "$evidence/coverage_execution.log" -Encoding utf8
if($coverageExit -ne 0 -or ($coverageOut -join "`n") -match 'Execution: Error') {
  throw 'Coverage run failed; inspect coverage_execution.log'
}
$coverage = @()
$percentages = @($coverageOut | Where-Object {$_ -match '^Coverage = ([0-9.]+)%'})
if($percentages.Count -ne $sources.Count){throw 'Missing native VDMJ coverage summaries'}
foreach($index in 0..($sources.Count-1)) {
  $nativeMatch = [regex]::Match($percentages[$index],'^Coverage = ([0-9.]+)%')
  $file = [IO.Path]::GetFileName($sources[$index])
  $section = [regex]::Match(($coverageOut -join "`n"),'(?ms)Test coverage for [^\r\n]*' +
    [regex]::Escape($file) + ':\r?\n(?<body>.*?)Coverage =').Groups['body'].Value
  $hitLines = [regex]::Matches($section,'(?m)^\+ ').Count
  $missLines = [regex]::Matches($section,'(?m)^- ').Count
  $coverage += [ordered]@{file=[IO.Path]::GetFileName($sources[$index]);
    native_vdmj_percent=[double]::Parse($nativeMatch.Groups[1].Value,[Globalization.CultureInfo]::InvariantCulture);
    covered_lines=$hitLines;total_executable_lines=$hitLines+$missLines;
    metric='VDMJ native executable-source-line coverage, 40 behavioural cases only';
    note='.cov stores hits only; its row count is NOT a coverage denominator'}
}
$coverage | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath "$evidence/coverage.json" -Encoding utf8
$production = @($sources | Where-Object {[IO.Path]::GetFileName($_) -ne 'TestSAT.vdmpp'})
$proof = @(& $JavaPath @common '-p' @production 2>&1)
$proof | Set-Content -LiteralPath "$evidence/proof_obligations.log" -Encoding utf8
Write-Output 'Coverage and proof-obligation inventory saved. No proof discharge claimed.'
