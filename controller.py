from flask import Flask, jsonify, request
import asyncio

import olxApi
import allegroApi
import allegroLokalneApi
# import xkomApi  # Commented out as it's incomplete
from validComponentsApi.extract_details import extract_cpu_details, extract_gpu_details

app = Flask(__name__)

@app.route('/components', methods=['GET'])
def get_components():
    """Get components from all APIs with optional category filtering"""
    category = request.args.get('category', None)
    source = request.args.get('source', 'all')  # all, olx, allegro, allegro_lokalne
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    all_components = {}
    
    try:
        # Scrape from different sources based on request
        if source == 'all' or source == 'olx':
            print("Scraping OLX...")
            olx_data = loop.run_until_complete(olxApi.main())
            all_components['olx'] = organize_by_category(olx_data)
        
        if source == 'all' or source == 'allegro':
            print("Scraping Allegro...")
            allegro_data = loop.run_until_complete(allegroApi.main())
            all_components['allegro'] = organize_by_category(allegro_data)
        
        if source == 'all' or source == 'allegro_lokalne':
            print("Scraping Allegro Lokalne...")
            allegro_lokalne_data = loop.run_until_complete(allegroLokalneApi.main())
            all_components['allegro_lokalne'] = organize_by_category(allegro_lokalne_data)
        
        # Apply CPU details extraction to processor categories
        all_components = apply_cpu_extraction(all_components)
        
        # Apply GPU details extraction to graphics card categories
        all_components = apply_gpu_extraction(all_components)
        
        # Filter by category if specified
        if category:
            filtered_components = {}
            for source_name, source_data in all_components.items():
                if category in source_data:
                    filtered_components[source_name] = {category: source_data[category]}
                else:
                    filtered_components[source_name] = {}
            return jsonify(filtered_components)
        
        return jsonify(all_components)
    
    except Exception as e:
        return jsonify({"error": f"Failed to scrape data: {str(e)}"}), 500
    
    finally:
        loop.close()

@app.route('/components/cpu', methods=['GET'])
def get_cpu_components():
    """Get CPU components with extracted details from all sources"""
    source = request.args.get('source', 'all')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    cpu_components = {}
    
    try:
        if source == 'all' or source == 'olx':
            print("Scraping OLX CPUs...")
            olx_data = loop.run_until_complete(olxApi.main())
            olx_cpus = [item for item in olx_data if item.get('category') == 'procesor']
            if olx_cpus:
                cpu_components['olx'] = extract_cpu_details(olx_cpus)
        
        if source == 'all' or source == 'allegro':
            print("Scraping Allegro CPUs...")
            allegro_data = loop.run_until_complete(allegroApi.main())
            allegro_cpus = [item for item in allegro_data if item.get('category') == 'procesor']
            if allegro_cpus:
                cpu_components['allegro'] = extract_cpu_details(allegro_cpus)
        
        if source == 'all' or source == 'allegro_lokalne':
            print("Scraping Allegro Lokalne CPUs...")
            allegro_lokalne_data = loop.run_until_complete(allegroLokalneApi.main())
            allegro_lokalne_cpus = [item for item in allegro_lokalne_data if item.get('category') == 'procesor']
            if allegro_lokalne_cpus:
                cpu_components['allegro_lokalne'] = extract_cpu_details(allegro_lokalne_cpus)
        
        return jsonify(cpu_components)
    
    except Exception as e:
        return jsonify({"error": f"Failed to scrape CPU data: {str(e)}"}), 500
    
    finally:
        loop.close()

@app.route('/components/gpu', methods=['GET'])
def get_gpu_components():
    """Get GPU components with extracted details from all sources"""
    source = request.args.get('source', 'all')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    gpu_components = {}
    
    try:
        if source == 'all' or source == 'olx':
            print("Scraping OLX GPUs...")
            olx_data = loop.run_until_complete(olxApi.main())
            olx_gpus = [item for item in olx_data if item.get('category') == 'karta graficzna']
            if olx_gpus:
                gpu_components['olx'] = extract_gpu_details(olx_gpus)
        
        if source == 'all' or source == 'allegro':
            print("Scraping Allegro GPUs...")
            allegro_data = loop.run_until_complete(allegroApi.main())
            allegro_gpus = [item for item in allegro_data if item.get('category') == 'karta graficzna']
            if allegro_gpus:
                gpu_components['allegro'] = extract_gpu_details(allegro_gpus)
        
        if source == 'all' or source == 'allegro_lokalne':
            print("Scraping Allegro Lokalne GPUs...")
            allegro_lokalne_data = loop.run_until_complete(allegroLokalneApi.main())
            allegro_lokalne_gpus = [item for item in allegro_lokalne_data if item.get('category') == 'karta graficzna']
            if allegro_lokalne_gpus:
                gpu_components['allegro_lokalne'] = extract_gpu_details(allegro_lokalne_gpus)
        
        return jsonify(gpu_components)
    
    except Exception as e:
        return jsonify({"error": f"Failed to scrape GPU data: {str(e)}"}), 500
    
    finally:
        loop.close()

def organize_by_category(data):
    """Organize scraped data by category"""
    organized = {}
    for item in data:
        category = item.get('category', 'unknown')
        if category not in organized:
            organized[category] = []
        organized[category].append(item)
    return organized

def apply_cpu_extraction(all_components):
    """Apply CPU details extraction to processor categories across all sources"""
    for source_name, source_data in all_components.items():
        if 'procesor' in source_data:
            cpu_items = source_data['procesor']
            extracted_cpus = extract_cpu_details(cpu_items)
            source_data['procesor_extracted'] = extracted_cpus
    return all_components

def apply_gpu_extraction(all_components):
    """Apply GPU details extraction to graphics card categories across all sources"""
    for source_name, source_data in all_components.items():
        if 'karta graficzna' in source_data:
            gpu_items = source_data['karta graficzna']
            extracted_gpus = extract_gpu_details(gpu_items)
            source_data['karta_graficzna_extracted'] = extracted_gpus
    return all_components

@app.route('/shops', methods=['GET'])
def get_all_shops():
    """Get all components organized by shop (olx, allegro, allegro_lokalne)"""
    include_extracted = request.args.get('extracted', 'true').lower() == 'true'
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    shops_data = {}
    
    try:
        print("Scraping all shops...")
        
        # Scrape OLX
        print("📱 Scraping OLX...")
        olx_data = loop.run_until_complete(olxApi.main())
        shops_data['olx'] = {
            "shop_name": "OLX",
            "shop_url": "https://olx.pl",
            "total_items": len(olx_data),
            "categories": organize_by_category(olx_data)
        }
        
        # Scrape Allegro
        print("🛒 Scraping Allegro...")
        allegro_data = loop.run_until_complete(allegroApi.main())
        shops_data['allegro'] = {
            "shop_name": "Allegro",
            "shop_url": "https://allegro.pl",
            "total_items": len(allegro_data),
            "categories": organize_by_category(allegro_data)
        }
        
        # Scrape Allegro Lokalne
        print("🏪 Scraping Allegro Lokalne...")
        allegro_lokalne_data = loop.run_until_complete(allegroLokalneApi.main())
        shops_data['allegro_lokalne'] = {
            "shop_name": "Allegro Lokalne",
            "shop_url": "https://allegrolokalnie.pl",
            "total_items": len(allegro_lokalne_data),
            "categories": organize_by_category(allegro_lokalne_data)
        }
        
        # Apply extraction if requested
        if include_extracted:
            print("🔍 Applying details extraction...")
            for shop_key, shop_data in shops_data.items():
                # Apply CPU extraction
                if 'procesor' in shop_data['categories']:
                    cpu_items = shop_data['categories']['procesor']
                    extracted_cpus = extract_cpu_details(cpu_items)
                    shop_data['categories']['procesor_extracted'] = extracted_cpus
                
                # Apply GPU extraction
                if 'karta graficzna' in shop_data['categories']:
                    gpu_items = shop_data['categories']['karta graficzna']
                    extracted_gpus = extract_gpu_details(gpu_items)
                    shop_data['categories']['karta_graficzna_extracted'] = extracted_gpus
        
        # Add summary statistics
        summary = {
            "total_shops": len(shops_data),
            "shops_scraped": list(shops_data.keys()),
            "total_items_across_all_shops": sum(shop['total_items'] for shop in shops_data.values()),
            "categories_found": set()
        }
        
        # Collect all unique categories
        for shop_data in shops_data.values():
            summary["categories_found"].update(shop_data['categories'].keys())
        summary["categories_found"] = sorted(list(summary["categories_found"]))
        
        return jsonify({
            "summary": summary,
            "shops": shops_data
        })
    
    except Exception as e:
        return jsonify({"error": f"Failed to scrape shops data: {str(e)}"}), 500
    
    finally:
        loop.close()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "PC Build Scraper API is running"})

@app.route('/', methods=['GET'])
def home():
    """API documentation endpoint"""
    return jsonify({
        "message": "PC Build Scraper API",
        "endpoints": {
            "/shops": "🛒 Get all components organized by shop (optional: ?extracted=false)",
            "/components": "Get all components (optional: ?category=procesor&source=olx)",
            "/components/cpu": "Get CPU components with extracted details (optional: ?source=allegro)",
            "/components/gpu": "Get GPU components with extracted details (optional: ?source=all)",
            "/health": "Health check"
        },
        "recommended_endpoint": {
            "url": "/shops",
            "description": "Best endpoint to get all components organized by shop",
            "example": "GET /shops - Returns all components from all shops with extraction"
        },
        "supported_categories": [
            "procesor", "karta graficzna", "ram", "case", 
            "storage", "power_Supply", "motherboard"
        ],
        "supported_sources": ["olx", "allegro", "allegro_lokalne", "all"]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
