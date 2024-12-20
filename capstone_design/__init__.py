from flask import Flask
from flask_pymongo import PyMongo
import os
from pymongo.mongo_client import MongoClient
#uri = "mongodb+srv://ju010320:capstone_poohanghang@poohanghang.443rb.mongodb.net/?retryWrites=true&w=majority&appName=poohanghang"
#mongo = MongoClient(uri)


# MongoDB 초기화
mongo = PyMongo()

def create_app():
    app = Flask(__name__)

    # Flask 앱 설정
    #app.config['MONGO_URI'] = 'mongodb+srv://ju010320:capstone_poohanghang@poohanghang.443rb.mongodb.net/'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/poohanghang'
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.config['MODEL_FOLDER'] = os.path.join(os.getcwd(), 'models')
    #app.register_blueprint(upload_bp, url_prefix='/api')

    # 필요한 폴더 생성
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

    # MongoDB 초기화
    mongo.init_app(app)

    # 블루프린트 등록
    from .routes.upload import upload_bp
    from .routes.records import records_bp
    from .routes.auth import auth_bp
    from .routes.patient import patient_bp

    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(records_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(patient_bp, url_prefix='/api')


    return app
