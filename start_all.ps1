# JWBuddy 一键启动脚本
Write-Host "=== JWBuddy 服务启动 ===" -ForegroundColor Cyan

$BackendDir = "E:\mysql\AI智能体\jwbuddy\backend"
$DesktopDir = "E:\mysql\AI智能体\jwbuddy\desktop"
$Python = "$BackendDir\.venv\Scripts\python.exe"

# 1. 后端 API (端口 8000)
Write-Host "[1/3] 启动后端 API (8000)..." -ForegroundColor Yellow
$backend = Start-Process -FilePath $Python -ArgumentList @(
    "-c", "import sys,os; sys.path.insert(0,'$BackendDir'); sys.path.insert(0,'$BackendDir/src'); os.chdir('$BackendDir'); import uvicorn; from jwbuddy.main import app; uvicorn.run(app,host='0.0.0.0',port=8000)"
) -WindowStyle Hidden -PassThru
Write-Host "  PID: $($backend.Id)" -ForegroundColor Green

Start-Sleep -Seconds 2

# 2. Web 前端 (端口 8080)
Write-Host "[2/3] 启动 Web 前端 (8080)..." -ForegroundColor Yellow
$web = Start-Process -FilePath "python" -ArgumentList @(
    "-m", "http.server", "8080", "-d", "$DesktopDir\dist"
) -WindowStyle Hidden -PassThru
Write-Host "  PID: $($web.Id)" -ForegroundColor Green

# 3. MCP Server (端口 8001)
Write-Host "[3/3] 启动 MCP Server (8001)..." -ForegroundColor Yellow
$mcp = Start-Process -FilePath $Python -ArgumentList @(
    "-c", "import sys,os; sys.path.insert(0,'$BackendDir'); sys.path.insert(0,'$BackendDir/src'); os.chdir('$BackendDir'); import uvicorn; from jwbuddy.mcp.server import MCPServer; from jwbuddy.mcp.protocol import MCPRequest; from jwbuddy.main import init_tools; init_tools(); from fastapi import FastAPI,Request; app=FastAPI(); _mcp=MCPServer(); @app.post('/mcp'); async def mcp_endpoint(r:Request): b=await r.json(); resp=await _mcp.handle_request(MCPRequest(**b)); return resp.model_dump(exclude_none=True); @app.get('/health'); async def health(): return {'status':'ok','app':'JWBuddy MCP'}; uvicorn.run(app,host='0.0.0.0',port=8001)"
) -WindowStyle Hidden -PassThru
Write-Host "  PID: $($mcp.Id)" -ForegroundColor Green

Start-Sleep -Seconds 3

# 验证
Write-Host "`n=== 验证 ===" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host "  8000 后端: $($r.Content)" -ForegroundColor Green
} catch { Write-Host "  8000 后端: 失败!" -ForegroundColor Red }

try {
    $r = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing
    Write-Host "  8001 MCP:   $($r.Content)" -ForegroundColor Green
} catch { Write-Host "  8001 MCP:   失败!" -ForegroundColor Red }

try {
    $r = Invoke-WebRequest -Uri "http://localhost:8080/" -UseBasicParsing
    Write-Host "  8080 Web:   HTTP $($r.StatusCode)" -ForegroundColor Green
} catch { Write-Host "  8080 Web:   失败!" -ForegroundColor Red }

Write-Host "`n=== 启动完成 ===" -ForegroundColor Cyan
Write-Host "Web UI:   http://localhost:8080/" -ForegroundColor Cyan
Write-Host "API:      http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "MCP:      http://localhost:8001/mcp" -ForegroundColor Cyan
