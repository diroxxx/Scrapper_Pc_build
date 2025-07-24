from flask import Flask, jsonify, request
import asyncio

import olxApi
import allegroApi
import allegroLokalneApi
# import xkomApi  # Commented out as it's incomplete

app = Flask(__name__)

CATEGORIES = [
    "processor", "graphics_card", "ram", "case", "storage", "power_supply", "motherboard"
]

app = Flask(__name__)

@app.route('/comp', methods=['GET'])
def get_comp():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(olxApi.main())
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
