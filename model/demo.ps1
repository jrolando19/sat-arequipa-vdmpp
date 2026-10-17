param(
  [string]$JavaPath = 'java',
  [string]$JarPath = "$PSScriptRoot/tools/vdmj-suite-4.7.0/vdmj-4.7.0.jar",
  [string]$EvidenceDir = "$PSScriptRoot/../evidence_reproduced"
)
$ErrorActionPreference = 'Stop'
$sources = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.vdmpp' | Sort-Object Name | ForEach-Object FullName)
$commands = @(
  'set pre on', 'set post on', 'set inv on', 'set dtc on',
  'create demo := new TestSAT().Base()',
  'print demo.Ver(TestSAT`q)',
  'print demo.RecibirLectura(TestSAT`E(1,TestSAT`s,TestSAT`q,1,99,80,4))',
  'print demo.Ver(TestSAT`q)',
  'print demo.VerAvisos()',
  'print demo.RecibirLectura(TestSAT`E(2,TestSAT`s,TestSAT`q,2,100,40,3))',
  'print demo.Ver(TestSAT`q)',
  'print demo.RegistrarConfirmacion(TestSAT`admin,TestSAT`q,TestSAT`E(2,TestSAT`s,TestSAT`q,2,100,40,3).id)',
  'print demo.Ver(TestSAT`q)',
  'print demo.AplicarDescenso(TestSAT`admin,TestSAT`q)',
  'print demo.Ver(TestSAT`q)',
  'print demo.VerAvisos()',
  'quit'
)
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
$commands | Set-Content -LiteralPath "$EvidenceDir/demo_commands.txt" -Encoding utf8
$out = @($commands | & $JavaPath '-jar' $JarPath '-vdmpp' '-r' 'vdm10' '-strict' '-c' 'UTF-8' '-i' @sources 2>&1)
$exitCode = $LASTEXITCODE
$out | Set-Content -LiteralPath "$EvidenceDir/demo.log" -Encoding utf8
$out
if($exitCode -ne 0 -or ($out -join "`n") -match 'Execution: Error') {exit 1}
