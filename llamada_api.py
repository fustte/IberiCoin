import requests                                                     #Para realizar solicitudes HTTP a la API.
import json                                                         #Para trabajar con archivos y datos en formato JSON.
from dotenv import load_dotenv                                      #Para cargar las variables de entorno desde un archivo .env.
import os                                                           #Para interactuar con las variables de entorno del sistema.

# Cargar las variables de entorno desde el archivo .env
load_dotenv()


# Obtiene la clave API desde las variables de entorno y elimina posibles espacios en blanco.
API_KEY = os.getenv('API_KEY').strip()
COINAPI_URL = os.getenv('COINAPI_URL').strip()


# Lista de criptomonedas a consultar
base_currency = 'EUR'
target_cryptocurrencies = ['BTC', 'ETH', 'USDT', 'ADA', 'SOL', 'XRP', 'DOT', 'DOGE', 'SHIB']


# base_currency: Define la moneda base para las conversiones (EUR).
# target_cryptocurrencies: Lista de criptomonedas objetivo para las cuales se quieren obtener las tasas de cambio.


def get_coin_prices(base_currency, target_cryptocurrencies):
    prices = {}       # Inicializa un diccionario vacío para almacenar las tasas de cambio obtenidas.
    
    # Leer los precios existentes desde el archivo JSON
    try:
        with open('prices.json', 'r') as f:                 #Abre el archivo prices.json en modo lectura.
            prices = json.load(f)                           #Carga el contenido del archivo JSON en el diccionario prices.
    except FileNotFoundError:                               #Si el archivo no se encuentra, inicializa prices como un diccionario vacío.
        prices = {}

    
    #Solicitud a la API para Obtener las Tasas de Cambio
    
    #Hacer una sola llamada a la API para obtener las tasas de cambio de base_currency a todas las target_cryptocurrencies
    
    url = f'{COINAPI_URL}/{base_currency}?apikey={API_KEY}'           #Construye la URL para hacer la solicitud GET a la API de CoinAPI.
    response = requests.get(url)                   #Realiza la solicitud GET a la API.
    if response.status_code == 200:                 #Verifica si la solicitud fue exitosa (código de estado 200).
        data = response.json()                     #Convierte la respuesta de la API en formato JSON a un diccionario de Python.
        for rate in data['rates']:                      #Itera sobre cada tasa de cambio en la respuesta de la API.
            if rate['asset_id_quote'] in target_cryptocurrencies:   #Verifica si la criptomoneda de destino está en la lista de criptomonedas objetivo.
                try:
                    rate_value = 1 / float(rate['rate'])            #Convierte la tasa de cambio de EUR a la criptomoneda (invirtiendo la tasa).
                    prices[rate['asset_id_quote']] = rate_value         #Almacena la tasa de cambio en el diccionario prices.
                
                #Manejo de Errores: ValueError: Error al convertir la tasa de cambio, TypeError: Error en el tipo de datos, ZeroDivisionError: Error de división por cero.
                
                except (ValueError, TypeError, ZeroDivisionError) as e:
                    print(f"Error al convertir la tasa de {rate['asset_id_quote']}: {e}")
        
    else:
        print(f"Error al obtener los precios: {response.status_code}")          ##Si la solicitud no fue exitosa, imprime un mensaje de error con el código de estado.

    
    # Guardar los precios actualizados en el archivo JSON

    with open('prices.json', 'w') as f:             #Abre el archivo prices.json en modo escritura.
        json.dump(prices, f)                  #Escribe los precios actualizados en el archivo JSON.
    
    return prices                   #Retorna el diccionario prices que contiene las tasas de cambio obtenidas y actualizadas.




