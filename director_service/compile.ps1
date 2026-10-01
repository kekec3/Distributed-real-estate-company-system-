param ([string]$file_path = "voting.sol")

Remove-Item ./director_service/output -Recurse -ErrorAction Ignore
New-Item -ItemType Directory -Path ./director_service/output | Out-Null

docker run --rm `
  -v "${PWD}/director_service:/sources" `
  ethereum/solc:0.8.18 `
  -o /sources/output --abi --bin /sources/$file_path

Write-Host "Compiled. Output:"
Get-ChildItem ./director_service/output