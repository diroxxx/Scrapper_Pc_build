from flask import Flask, jsonify, request
import asyncio

import olxApi
import allegroApi
import allegroLokalneApi
# import xkomApi  # Commented out as it's incomplete
from validComponentsApi.extract_details import extract_cpu_info

app = Flask(__name__)


CATEGORIES = {
    "processor", "graphics_card", "ram", "case", "storage", "power_supply", "motherboard"
}


@app.route('/components', methods=['GET'])
def get_components():
    """Get components from all APIs"""
    all_components = {cat: [] for cat in CATEGORIES}    
    olxApi_components = asyncio.run(olxApi.main())
    # allegroApi_components = asyncio.run(allegroApi.main())
    # allegroLokalneApi_components = asyncio.run(allegroLokalneApi.main())
    # xkomApi_components = asyncio.run(xkomApi.main())  # Commented out
    # for category in CATEGORIES:
        # all_components[category].extend(allegroApi_components[category])
        # all_components[category].extend(allegroLokalneApi_components[category])
        # all_components[category].extend(xkomApi_components[category])  # Commented out

    # for key, component in all_components.items():
    #     if key == "graphics card":
    #         for comp in component:
    #             comp.update(extract_gpu_details(comp["name"]))


    # for component in all_components:
    #     if component['category'] = 
        
    
    # loop.close()
    # return jsonify(all_components)
    return jsonify(olxApi_components)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
