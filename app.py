import cloudinary
import cloudinary.uploader
from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from data import products  # Import products from data.py

# Load environment variables from .env file
load_dotenv()

# Initialize Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('API_KEY'),
    api_secret=os.getenv('API_SECRET')
)

app = Flask(__name__)

# Route to get all products
@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(products)

# Route to get a single product by ID
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((prod for prod in products if prod['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"message": "Product not found"}), 404

# Route to upload an image to Cloudinary
def upload_image(image_file):
    response = cloudinary.uploader.upload(image_file)
    return response['secure_url']

# Route to add a new product with image upload
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    images = []
    
    # Handle image upload
    if 'images' in data:
        for image in data['images']:
            image_url = upload_image(image)
            images.append(image_url)
    
    new_product = {
        "id": len(products) + 1,
        "name": data['name'],
        "description": data['description'],
        "brand": data['brand'],
        "categories": data['categories'],
        "images": images
    }
    
    products.append(new_product)
    return jsonify(new_product), 201

# Route to update a product
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = next((prod for prod in products if prod['id'] == product_id), None)
    if product:
        data = request.json
        images = []
        
        # Handle image upload
        if 'images' in data:
            for image in data['images']:
                image_url = upload_image(image)
                images.append(image_url)
        
        product.update({
            "name": data.get("name", product["name"]),
            "description": data.get("description", product["description"]),
            "brand": data.get("brand", product["brand"]),
            "categories": data.get("categories", product["categories"]),
            "images": images or product["images"]
        })
        return jsonify(product)
    
    return jsonify({"message": "Product not found"}), 404

# Route to delete a product
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    global products
    products = [prod for prod in products if prod['id'] != product_id]
    return jsonify({"message": "Product deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)

