"""
/***********************************************************
* Author       : lzw
* EMail        : lizhiwen566@gmail.com
* Last modified: 2021-02-22 15:10
* Filename     : app.py
* Description  : demo one
**********************************************************/
"""
# request 获得网页接收的数据
from flask import Flask

app = Flask(__name__)
app.debug = True

from .main import main as main_blueprint
app.register_blueprint(main_blueprint, static_fold='static')
