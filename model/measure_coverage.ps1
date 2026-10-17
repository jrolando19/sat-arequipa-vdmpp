param(
  [string]$JavaPath = 'java',
  [string]$JarPath = "$PSScriptRoot/tools/vdmj-suite-4.7.0/vdmj-4.7.0.jar",
  [string]$EvidenceDir = "$PSScriptRoot/../evidence_reproduced"
)
$ErrorActionPreference = 'Stop'
$sources = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.vdmpp' | Sort-Object Name | ForEach-Object FullName)
$evidence = [IO.Path]::GetFullPath($EvidenceDir)
$coverageDir = Join-Path $evidence 'coverage'
New-Item -ItemType Directory -Force -Path $coverageDir | Out-Null
$pathForCommand = $coverageDir -replace '\\','/'
$commands = @('set pre on','set post on','set inv on','set dtc on') +
  @(1..40 | ForEach-Object {'print new TestSAT().T{0:00}()' -f $_}) +
  @("coverage write $pathForCommand") +
  @($sources | ForEach-Object {'coverage ' + ($_ -replace '\\','/')}) + @('quit')
$out = @($commands | & $JavaPath '-jar' $JarPath '-vdmpp' '-r' 'vdm10' '-strict' '-c' 'UTF-8' '-i' @sources 2>&1)
$code = $LASTEXITCODE
$out | Set-Content -LiteralPath "$evidence/coverage_execution.log" -Encoding utf8
$percentages = @($out | Where-Object {$_ -match '^Coverage = ([0-9.]+)%'})
if($code -ne 0 -or $percentages.Count -ne $sources.Count -or
  ($out -join "`n") -match 'Execution: Error|not loaded|not a directory'){
  throw 'Native coverage collection failed'
}
$coverage = @()
foreach($index in 0..($sources.Count-1)) {
  $native = [regex]::Match($percentages[$index],'^Coverage = ([0-9.]+)%')
  $file = [IO.Path]::GetFileName($sources[$index])
  $section = [regex]::Match(($out -join "`n"),'(?ms)Test coverage for [^\r\n]*' +
    [regex]::Escape($file) + ':\r?\n(?<body>.*?)Coverage =').Groups['body'].Value
  $hitLines = [regex]::Matches($section,'(?m)^\+ ').Count
  $missLines = [regex]::Matches($section,'(?m)^- ').Count
  $coverage += [ordered]@{file=[IO.Path]::GetFileName($sources[$index]);
    native_vdmj_percent=[double]::Parse($native.Groups[1].Value,[Globalization.CultureInfo]::InvariantCulture);
    covered_lines=$hitLines;total_executable_lines=$hitLines+$missLines;
    metric='VDMJ native executable-source-line coverage, 40 behavioural cases only';
    note='.cov stores hits only; its row count is NOT a coverage denominator'}
}
$coverage | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath "$evidence/coverage.json" -Encoding utf8
$coverage | ForEach-Object {Write-Output "$($_.file) $($_.native_vdmj_percent)%"}
