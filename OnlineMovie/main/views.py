from flask import jsonify

from main import app


@app.errorhandler(404)
def page_not_fonud(e):
    return jsonify({"message": "页面未找到！"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"message": "服务器异常！"}), 500
#docker run  --name my_nginx -p 9001:80  -v /Users/apple/data/nginx/conf/nginx.conf:/etc/nginx/nginx.conf  -v /Users/apple/data/nginx/log:/var/log/nginx  -v /Users/apple/data/nginx/html:/usr/share/nginx/html -d nginx