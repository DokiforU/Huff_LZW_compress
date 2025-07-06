# run.py

from web_app import app # 从 web_app 包导入创建的 app 实例

if __name__ == '__main__':
    # 启动 Flask 开发服务器
    debug=True # 会在代码更改时自动重载服务器，并提供交互式调试器
    # host='0.0.0.0' 允许局域网内其他设备访问
    # port=5000 是默认端口，可以修改
    app.run(debug=True, host='0.0.0.0', port=5001)