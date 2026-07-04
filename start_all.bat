@echo off
chcp 65001 >nul
echo === JWBuddy 服务启动 ===

set BACKEND=E:\mysql\AI智能体\jwbuddy\backend
set DESKTOP=E:\mysql\AI智能体\jwbuddy\desktop
set PYTHON=%BACKEND%\.venv\Scripts\python.exe

echo [1/3] 启动后端 API (8000)...
start /B "" "%PYTHON%" -c "import sys,os; sys.path.insert(0,'%BACKEND%'); sys.path.insert(0,'%BACKEND%/src'); os.chdir('%BACKEND%'); import uvicorn; from jwbuddy.main import app; uvicorn.run(app,host='0.0.0.0',port=8000)"

timeout /t 3 /nobreak >nul

echo [2/3] 启动 Web 前端 (8080)...
start /B "" python -m http.server 8080 -d "%DESKTOP%\dist"

echo [3/3] 启动 MCP Server (8001)...
start /B "" "%PYTHON%" -c "import sys,os; sys.path.insert(0,'%BACKEND%'); sys.path.insert(0,'%BACKEND%/src'); os.chdir('%BACKEND%'); import uvicorn; from jwbuddy.mcp.server import MCPServer; from jwbuddy.mcp.protocol import MCPRequest; from jwbuddy.main import init_tools; init_tools(); from fastapi import FastAPI,Request; app=FastAPI(); _mcp=MCPServer(); @app.post('/mcp'); async def mcp_endpoint(r:Request): b=await r.json(); resp=await _mcp.handle_request(MCPRequest(**b)); return resp.model_dump(exclude_none=True); @app.get('/health'); async def health(): return {'status':'ok','app':'JWBuddy MCP'}; uvicorn.run(app,host='0.0.0.0',port=8001)"

timeout /t 4 /nobreak >nul

echo.
echo === 验证 ===
powershell -Command "try { $r=Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing; Write-Host '  8000 后端: '$r.Content -ForegroundColor Green } catch { Write-Host '  8000 后端: 失败!' -ForegroundColor Red }"
powershell -Command "try { $r=Invoke-WebRequest -Uri 'http://localhost:8001/health' -UseBasicParsing; Write-Host '  8001 MCP:   '$r.Content -ForegroundColor Green } catch { Write-Host '  8001 MCP:   失败!' -ForegroundColor Red }"
powershell -Command "try { $r=Invoke-WebRequest -Uri 'http://localhost:8080/' -UseBasicParsing; Write-Host '  8080 Web:   HTTP '$r.StatusCode -ForegroundColor Green } catch { Write-Host '  8080 Web:   失败!' -ForegroundColor Red }"

echo.
echo === 启动完成 ===
echo Web UI:   http://localhost:8080/
echo API:      http://localhost:8000/docs
echo MCP:      http://localhost:8001/mcp
pause
