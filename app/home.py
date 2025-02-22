from flask import Blueprint, render_template, current_app
import requests
import os
from dotenv import load_dotenv

bp = Blueprint('home', __name__)

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('INVENTREE_API_TOKEN')
INVENTREE_URL = os.getenv('INVENTREE_BASE_URL')
print(f"API_KEY: {API_KEY}, INVENTREE_URL: {INVENTREE_URL}")  # Debugging: Print the loaded environment variables

# Set up the headers with your API token
headers = {
    'Authorization': f'Token {API_KEY}',
    'Content-Type': 'application/json'
}

def get_all_selection():
    url = f'{INVENTREE_URL}/api/selection/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

# Function to get all subcategories for a given parent category ID
def get_all_subcategories(parentid):
    url = f'{INVENTREE_URL}/api/part/category/?parent={parentid}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

@bp.route('/', methods=['GET', 'POST'])
def home():
    parentid = 196  # Set parent id where fasteners type are located
    #subcatlist = get_all_subcategories(parentid)
    fastener_type = get_all_subcategories(parentid)
    current_app.config['FASTENER_TYPE'] = fastener_type
    
    selectionlist = get_all_selection()
    print(f'call functions')
    return render_template('home.html', selectionlist=selectionlist, fastener_type=fastener_type)
