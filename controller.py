from flask import Flask, jsonify
import asyncio

from unicodedata import category

import olxApi

app = Flask(__name__)

@app.route('/comp', methods=['GET'])
def get_comp():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(olxApi.main())
    if category in data:
        return jsonify(data[category])
    else:
        return jsonify({"error": "Nieznana kategoria"}), 404


if __name__ == '__main__':
    app.run(debug=True)
