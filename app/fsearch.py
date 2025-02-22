from flask import Blueprint, render_template, request, current_app
import requests
import os
from dotenv import load_dotenv

bp = Blueprint('fsearch', __name__)

API_KEY = os.getenv('INVENTREE_API_TOKEN')
INVENTREE_URL = os.getenv('INVENTREE_BASE_URL')
print(f"INVENTREE_URL: {INVENTREE_URL}")  # Debugging: Print the loaded environment variables

# Set up the headers with your API token
headers = {
    'Authorization': f'Token {API_KEY}',
    'Content-Type': 'application/json'
}

# List of possible first words
#fastener_type = ["vite", "bullone", "ranella", "dado"]

# List of possible head types and their corresponding abbreviations
tipo_testa = {
    "testa tonda": "tt",
    "testa piatta": "tp",
    "testa semitonda": "ts",
    "testa cilindrica": "tc",
    "testa esagonale": "hx"
}

# List of possible tipo impronta and their corresponding abbreviations
tipo_impronta = {
    "torx": "tx",
    "croce": "cr",
    "taglio": "ta",
    "esagonale": "hx"
}

# List of possible tipo materiale and their corresponding abbreviations
tipo_materiale = {
    "zincato": "zi",
    "inox": "ix",
    "nylon": "ny",
    "ottone": "ot",
    "rame": "rm",
    "gomma": "go",
    "zincato nero": "zn",
    "zincato giallo": "zg"
}

# List of possible diametro standard for bullone and dado
diametro_standard = ["M1", "M1.2", "M1.6", "M2", "M2.5", "M3", 
                     "M4", "M5", "M6", "M8", "M10", 
                     "M12", "M16", "M20", "M24"]

# List of possible tipo di dado and their corresponding abbreviations
tipo_dado = {
    "standard": "st",
    "autobloccante": "ab",
    "farfalla": "ff",
    "conico": "cn",
    "4punte": "4p",
    "legno": "le",
    "inserto plastica": "ip"
}

# List of possible ranella tipo and their corresponding abbreviations
ranella_tipo = {
    "piana": "pi",
    "spezzata": "sp",
    "dentata": "de",
    "rosetta": "ro"
}

# List of possible lengths
lunghezza_standard = ["1", "1.2", "1.5", "1.8", "2", "2.2", "2.5", "2.8", "3", "4", "5", "6",
                       "8", "10", "12", "15", "16", "20", "25", "30", "35", "40", "45", "50"]


def search_part(part_name):
    
    params = {
        'search': part_name
    }
    
    response = requests.get(f'{INVENTREE_URL}/api/part/', headers=headers, params=params)
    
    if response.status_code == 200:
        parts = response.json()
        return parts
    else:
        print(f'Error: {response.status_code}')
        return None

def get_stock_location(part_id):
    
    response = requests.get(f'{INVENTREE_URL}/api/stock/?part={part_id}', headers=headers)
    
    if response.status_code == 200:
        stock_items = response.json()
        for item in stock_items:
            location_id = item['location']
            location_response = requests.get(f'{INVENTREE_URL}/api/stock/location/{location_id}/', headers=headers)
            if location_response.status_code == 200:
                location_data = location_response.json()
                item['location_path'] = location_data['pathstring']
        return stock_items
    else:
        print(f'Error: {response.status_code}')
        return None

@bp.route('/fsearch', methods=['GET', 'POST'])
def fsearch():
        text_string = ""  # Initialize text_string
        parts = ""
        result = ""
        fastener_type = current_app.config.get('FASTENER_TYPE', [])

        if request.method == 'POST':   
            user_input = request.form.get('fastener_select')
            print(user_input)           
            if user_input == "Viti -Screws":
                v_diameter = request.form.get('vf_diameter')
                v_length = request.form.get('vf_length')
                v_head_type = request.form.get('vf_head_type')
                v_impronta = request.form.get('vf_impronta')
                v_materiale = request.form.get('vf_materiale')
                text_string = f"vite {v_diameter}x{v_length} {tipo_testa.get(v_head_type, 'unknown')}-{tipo_impronta.get(v_impronta, 'unknown')}-{tipo_materiale.get(v_materiale, 'unknown')}"
            elif user_input == "Bulloni - Bolt":
                b_diameter = request.form.get('bf_diameter')
                b_length = request.form.get('bf_length')
                b_head_type = request.form.get('bf_head_type')
                b_impronta = request.form.get('bf_impronta')
                b_materiale = request.form.get('bf_materiale')
                text_string = f"bullone {b_diameter}x{b_length} {tipo_testa.get(b_head_type, 'unknown')}-{tipo_impronta.get(b_impronta, 'unknown')}-{tipo_materiale.get(b_materiale, 'unknown')}"
            elif user_input == "Dadi - Nuts":
                d_diameter = request.form.get('df_diameter')
                d_tipo_dado = request.form.get('df_tipo_dado')
                d_materiale = request.form.get('df_materiale')
                text_string = f"dado {d_diameter} {tipo_dado.get(d_tipo_dado, 'unknown')}-{tipo_materiale.get(d_materiale, 'unknown')}"
            elif user_input == "Ranelle - Washers":
                r_internal_diameter = request.form.get('rf_internal_diameter')
                r_external_diameter = request.form.get('rf_external_diameter')
                r_thickness = request.form.get('rf_thickness')
                r_tipo = request.form.get('rf_ranella_type')
                r_materiale = request.form.get('rf_materiale')
                text_string = f"ranella {r_internal_diameter}x{r_external_diameter}x{r_thickness} {ranella_tipo.get(r_tipo, 'unknown')}-{tipo_materiale.get(r_materiale, 'unknown')}"
            else:
                text_string = "Invalid fastener type"
            
            parts = search_part(text_string)
            if parts:
                result = []
                for part in parts:
                    part_info = {
                        'name': part['name'],
                        'description': part['description'],
                        'in_stock': part['in_stock']
                    }
                    
                    if part['in_stock'] > 0:
                        stock_items = get_stock_location(part['pk'])
                        if stock_items:
                            part_info['stock_locations'] = [
                                {'location_path': item['location_path'], 'quantity': item['quantity']}
                                for item in stock_items
                            ]
                    result.append(part_info)
                
                return render_template('fsearch.html', text_string=text_string, fastener_type=fastener_type, diametro_standard=diametro_standard, lunghezza_standard=lunghezza_standard, tipo_testa=tipo_testa, tipo_impronta=tipo_impronta, tipo_materiale=tipo_materiale, tipo_dado=tipo_dado, ranella_tipo=ranella_tipo, parts=result)
            else:
                return render_template('fsearch.html', text_string=text_string, fastener_type=fastener_type, diametro_standard=diametro_standard, lunghezza_standard=lunghezza_standard, tipo_testa=tipo_testa, tipo_impronta=tipo_impronta, tipo_materiale=tipo_materiale, tipo_dado=tipo_dado, ranella_tipo=ranella_tipo, error='No parts found')
            
        return render_template('fsearch.html', text_string=text_string, fastener_type=fastener_type, diametro_standard=diametro_standard, lunghezza_standard=lunghezza_standard, tipo_testa=tipo_testa, tipo_impronta=tipo_impronta, tipo_materiale=tipo_materiale, tipo_dado=tipo_dado, ranella_tipo=ranella_tipo, parts=result)