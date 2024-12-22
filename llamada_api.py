import requests                                                     
import json                                                         
from dotenv import load_dotenv                                      
import os                                                           

# Cargar las variables de entorno desde el archivo .env
load_dotenv()


# Obtiene la clave API desde las variables de entorno y elimina posibles espacios en blanco.
API_KEY = os.getenv('API_KEY').strip()
COINAPI_URL = os.getenv('COINAPI_URL').strip()


# Lista de criptomonedas a consultar
base_currency = 'EUR'
target_cryptocurrencies = ['BTC', 'ETH', 'USDT', 'ADA', 'SOL', 'XRP', 'DOT', 'DOGE', 'SHIB']





def get_coin_prices(base_currency, target_cryptocurrencies):
    prices = {}
    
    # Leer los precios existentes desde el archivo JSON
    try:
        with open('prices.json', 'r') as f:
            prices = json.load(f)
    except FileNotFoundError:
        prices = {}

    
    #Solicitud a la API para Obtener las Tasas de Cambio
    
    #Hacer una sola llamada a la API para obtener las tasas de cambio de base_currency a todas las target_cryptocurrencies
    
    url = f'{COINAPI_URL}/{base_currency}?apikey={API_KEY}'           
    response = requests.get(url)                   
    if response.status_code == 200:                 
        data = response.json()                     
        for rate in data['rates']:                     
            if rate['asset_id_quote'] in target_cryptocurrencies:   
                try:
                    rate_value = 1 / float(rate['rate'])            
                    prices[rate['asset_id_quote']] = rate_value         
                
                
                
                except (ValueError, TypeError, ZeroDivisionError) as e:
                    print(f"Error al convertir la tasa de {rate['asset_id_quote']}: {e}")
        
    else:
        print(f"Error al obtener los precios: {response.status_code}")         

    
    # Guardar los precios actualizados en el archivo JSON

    with open('prices.json', 'w') as f:             
        json.dump(prices, f)                  
    
    return prices                   




