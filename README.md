# IberiCoin

## Descripción

**IberiCoin** es una aplicación de gestión de cartera de criptomonedas que permite a los usuarios añadir fondos, verificar el saldo, realizar intercambios y consultar movimientos. La aplicación está diseñada para ser fácil de usar e interactiva.

## Instalación

### Prerrequisitos

- Python 3.x
- SQLite
- [pip](https://pip.pypa.io/en/stable/)

### Instrucciones

1.  Clona este repositorio: https://github.com/fustte/IberiCoin.git
    
    git clone  
    cd ibericoin

2.  Crea un entorno virtual:
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`

3.  Instala las dependencias:
        #pip install -r requirements.txt

4.  Configura las variables de entorno:
    Crea un archivo .env en el directorio raíz del proyecto con el siguiente contenido:
        #DATABASE_URI_WALLET=carpeta_y_nombre_de_tu_base_de_datos.sqlite

#### Uso

1. Inicialización de la Base de Datos

Antes de usar la aplicación, asegúrate de inicializar la base de datos:
    #python init_wallet_db.py



2. Ejecución de la Aplicación:

Para iniciar la aplicación, ejecuta el archivo main.py:
    #python main.py

##### Opciones disponibles:

1. Añadir Fondos: Permite añadir fondos en EUR a la cartera.

2. Verificar Saldo: Consulta el saldo actual de todas las monedas en la cartera.

3. Realizar Intercambio: Realiza un intercambio de monedas (compra/venta).

4. Consultar Movimientos: Consulta todos los movimientos en la base de datos.

5. Salir: Salir de la aplicación.


##### Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más información.


###### Contacto

Para cualquier consulta, puedes contactarme en ramos.fuster.javier@gmail.com
