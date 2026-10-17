param([string]$EvidenceDir = "$PSScriptRoot/../evidence_reproduced")
$ErrorActionPreference = 'Stop'
$evidence = [IO.Path]::GetFullPath($EvidenceDir)
$results = Get-Content -Raw -LiteralPath "$evidence/results.json" | ConvertFrom-Json
$coverage = Get-Content -Raw -LiteralPath "$evidence/coverage.json" | ConvertFrom-Json
$proof = Get-Content -Raw -LiteralPath "$evidence/proof_obligations.log"
$status = @{}
foreach($match in [regex]::Matches($proof,'Proof Obligation \d+: \((\w+)\)')){
  $key = $match.Groups[1].Value
  if(-not $status.ContainsKey($key)){$status[$key]=0}
  $status[$key]++
}
$sourceHashes = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.vdmpp' |
  Sort-Object Name | ForEach-Object {Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName} |
  Select-Object @{Name='file';Expression={[IO.Path]::GetFileName($_.Path)}},Hash)
$evidenceHashes = @(Get-ChildItem -LiteralPath $evidence -File |
  Where-Object {$_.Name -ne 'freeze.json'} | Sort-Object Name |
  ForEach-Object {Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName} |
  Select-Object @{Name='file';Expression={[IO.Path]::GetFileName($_.Path)}},Hash)
$freeze = [ordered]@{
  project='Sistema de Alerta Temprana de Huaicos y Deslizamientos en Quebradas de Arequipa';
  author='Jordy Rolando Tejada Lazo';model_version='2.0.0'; client_date='2026-10-17';
  deadline_date='2026-10-20';deadline_time='not specified by user';
  production_classes=5;test_classes=1;behaviour_cases=$results.behavioural_cases;
  expected_negative_cases=$results.expected_negative_cases;passed=$results.passed;failed=$results.failed;
  dynamic_checks=$results.checks;native_line_coverage=$coverage;
  proof_obligations_generated=([regex]::Match($proof,'Generated (\d+) proof obligations').Groups[1].Value -as [int]);
  proof_status=$status;proof_obligations_discharged=0;
  source_sha256=$sourceHashes;evidence_sha256=$evidenceHashes;
  summary='Executed finite scenarios with dynamic contracts. Not exhaustive proof or geotechnical validation.'
}
$freeze | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath "$evidence/freeze.json" -Encoding utf8
Write-Output "Frozen model2.0.0: $($results.passed)/$($results.total) conforming results; 80 undischarged obligations."
