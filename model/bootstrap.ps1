param([string]$Destination = "$PSScriptRoot/tools")
$ErrorActionPreference = 'Stop'
$url = 'https://github.com/nickbattle/vdmj/releases/download/4.7.0-release-fix/vdmj-suite-4.7.0-260414-distribution.zip'
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$zip = Join-Path $Destination 'vdmj.zip'
Invoke-WebRequest -Uri $url -OutFile $zip
if((Get-FileHash -Algorithm SHA256 -LiteralPath $zip).Hash -ne
  '0B224CC32B1C6DB296CE03E6AB1130461A09A2A4C5434D19D89246E42D569CE6') {
  throw 'Downloaded distribution checksum differs from the validated release. Do not continue.'
}
Expand-Archive -LiteralPath $zip -DestinationPath $Destination -Force
$jar = Join-Path $Destination 'vdmj-suite-4.7.0/vdmj-4.7.0.jar'
Get-FileHash -Algorithm SHA256 -LiteralPath $zip,$jar
if((Get-FileHash -Algorithm SHA256 -LiteralPath $jar).Hash -ne
  'F57EB06F0116E76916B789F683345398B0C95A1BD860FDC176CD119F2B89B19D') {
  throw 'VDMJ jar checksum differs from the validated release.'
}
Write-Output 'Run validate.ps1 -JavaPath <your-java-executable>; checks remain enabled by default.'
