# web_app/__init__.py

from flask import Flask
import os
from werkzeug.utils import import_string

# 创建 Flask 应用实例
# instance_relative_config=True 允许从 instance/ 文件夹加载配置（如果存在）
app = Flask(__name__, instance_relative_config=True)

# 设置最大文件上传大小为 100MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB in bytes
# 设置 Werkzeug 的文件大小限制
app.wsgi_app = import_string('werkzeug.middleware.proxy_fix.ProxyFix')(app.wsgi_app)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB in bytes
app.config['MAX_CONTENT_PATH'] = None  # 不限制文件路径长度

# 在创建 app 实例之后导入路由，以避免循环导入
# routes 模块需要 app 实例来进行路由注册 (@app.route)
from web_app import routes