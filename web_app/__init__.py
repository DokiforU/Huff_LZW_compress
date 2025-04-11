# web_app/__init__.py

from flask import Flask

# 创建 Flask 应用实例
# instance_relative_config=True 允许从 instance/ 文件夹加载配置（如果存在）
app = Flask(__name__, instance_relative_config=True)

# 在创建 app 实例之后导入路由，以避免循环导入
# routes 模块需要 app 实例来进行路由注册 (@app.route)
from web_app import routes