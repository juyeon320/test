import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from capstone_design import create_app

# Flask 애플리케이션 생성
app = create_app()
#app.config.from_object('satcounter_config')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
