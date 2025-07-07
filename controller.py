# from flask import Flask, jsonify
from flask_cors import CORS
# app = Flask(__name__)
# import olxApi
# @app.route('/comp', methods=['GET'])
# def get_comp():
#     return
#
# if __name__ == '__main__':
#     app.run(debug=True)
#
#
from flask import Flask, jsonify
import asyncio
import olxApi

app = Flask(__name__)

@app.route('/comp', methods=['GET'])
def get_comp():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(olxApi.main())
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
