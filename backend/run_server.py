"""JWBuddy 主服务启动脚本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import uvicorn
from jwbuddy.main import app
uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
