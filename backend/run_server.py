"""JWBuddy 主服务启动脚本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import uvicorn
from jwbuddy.main import app
PORT = int(os.environ.get("JWB_PORT", 8000))
uvicorn.run(app, host='0.0.0.0', port=PORT, log_level='info')
