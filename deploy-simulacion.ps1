<#
.SYNOPSIS
    Simulación de despliegue continuo - Sesión 3
.DESCRIPTION
    Clona el proyecto a una carpeta externa, ejecuta Docker Compose
    y valida que el servidor responda correctamente.
#>

$EXTERNAL_DIR = "C:\Users\adane\OneDrive\Desktop\8 SEMESTRE\GCS\deploy_simulado"
$REPO_URL = "https://github.com/IngAdancito/S8-TRABAJO-PR-CTICO-EXPERIMENTAL_4.git"
$BRANCH = "ci-setup"

Write-Host "=== SESIÓN 3 - Simulación de Despliegue Contínuo ===" -ForegroundColor Cyan

Write-Host "[1/4] Eliminando carpeta externa si existe..." -ForegroundColor Yellow
if (Test-Path $EXTERNAL_DIR) {
    Remove-Item -Path $EXTERNAL_DIR -Recurse -Force
}

Write-Host "[2/4] Clonando proyecto a carpeta externa..." -ForegroundColor Yellow
git clone --branch $BRANCH $REPO_URL $EXTERNAL_DIR
if (-not $?) {
    Write-Host "ERROR: No se pudo clonar el repositorio." -ForegroundColor Red
    exit 1
}

Write-Host "[3/4] Ejecutando Docker Compose en la carpeta externa..." -ForegroundColor Yellow
Set-Location $EXTERNAL_DIR
docker compose up -d --build
if (-not $?) {
    Write-Host "ERROR: Docker Compose falló." -ForegroundColor Red
    exit 1
}

Write-Host "[4/4] Validando que el servidor responda..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "`n=== DESPLIEGUE EXITOSO ===" -ForegroundColor Green
        Write-Host "El proyecto está corriendo en: http://localhost:8000/" -ForegroundColor Green
        Write-Host "Código de respuesta: $($response.StatusCode)" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Respuesta inesperada: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: No se pudo conectar al servidor." -ForegroundColor Red
    Write-Host "Revisá los logs con: docker compose logs web" -ForegroundColor Yellow
    exit 1
}

Set-Location -Path $EXTERNAL_DIR
Write-Host "`nComandos útiles:" -ForegroundColor Cyan
Write-Host "  docker compose logs web -f    # Ver logs" -ForegroundColor White
Write-Host "  docker compose down            # Detener servicios" -ForegroundColor White
