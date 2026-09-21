<#
.SYNOPSIS
  새 글 파일을 앞머리까지 채워서 만든다.

.EXAMPLE
  .\tools\new.ps1 "문자열 난독화 추적" -Labels Windows,난독화
  .\tools\new.ps1 "탐지 회피라는 말" -Kind 관찰          # 도구 안 쓰는 글
  .\tools\new.ps1 "EAC 핸들 스트리핑" -Slug eac-handle-strip -Tools "IDA, x64dbg"
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string] $Title,

  [string]   $Slug,
  [string[]] $Labels = @(),
  [string]   $Kind = "심층분석",
  [string]   $Subtitle,
  [string]   $Target,
  [string]   $Tools
)

$ErrorActionPreference = "Stop"

$root  = Split-Path -Parent $PSScriptRoot
$dir   = Join-Path $root "_reports"
$today = Get-Date -Format "yyyy-MM-dd"

if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }

if (-not $Slug) {
  $ascii = ($Title -replace '[^\p{IsBasicLatin}]', ' ').ToLower()
  $ascii = ($ascii -replace '[^a-z0-9]+', '-').Trim('-')
  if ($ascii.Length -ge 3) { $Slug = $ascii } else { $Slug = "r-" + (Get-Date -Format "yyyyMMdd") }
}

$path = Join-Path $dir "$Slug.md"
if (Test-Path $path) { throw "이미 있는 파일입니다: $path  ( -Slug 로 다른 이름을 주세요 )" }

$labelLine = if ($Labels.Count -gt 0) { "labels: [" + ($Labels -join ", ") + "]" } else { "labels: []" }
$subLine   = if ($Subtitle) { "subtitle: $Subtitle" } else { "# subtitle: 부제" }
$tgtLine   = if ($Target)   { "target: `"$Target`"" } else { "# target: `"sample.exe · SHA-256 ...`"   # 도구 안 쓰면 지워도 됨" }
$tlsLine   = if ($Tools)    { "tools: `"$Tools`"" }   else { "# tools: `"IDA Pro, x64dbg`"           # 도구 안 쓰면 지워도 됨" }

$body = @"
---
title: $Title
$subLine
date: $today
kind: $Kind
$labelLine
$tgtLine
$tlsLine
abstract: >
  두세 문장으로 요지. 목록과 검색에도 이 문장이 쓰인다.
# references:
#   - title: "기사 제목"
#     source: BleepingComputer
#     url: https://www.bleepingcomputer.com/...
#     date: $today
---

## 보도가 멈춘 자리

기사가 어디까지 다뤘고, 그 다음에 뭐가 비어 있는지. 인용은 이렇게 끼운다 <cite data-ref="1"></cite>.

## 확인한 것

## 미해결

-
"@

Set-Content -Path $path -Value $body -Encoding utf8
Write-Host ""
Write-Host "  만들었습니다:  $path"
Write-Host "  주소:          /r/$Slug/"
Write-Host "  미리보기:      python tools/preview.py -r $Slug"
Write-Host ""
Write-Host "  번호·목차·각주·개정 이력·참고자료 패널은 자동입니다. 본문만 쓰면 됩니다."
Write-Host ""
