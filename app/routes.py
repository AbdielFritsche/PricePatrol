
from flask import Blueprint, request, jsonify
from .web_scraper import *

# Crear el blueprint para las rutas
main_routes = Blueprint('main_routes', __name__)

# Definir las tiendas con sus URLs y selectores CSS específicos
STORES = [
    {
        "name": "Amazon Mexico",
        "search_url": "https://www.amazon.com.mx/s",
        "query_param": "k",  # Parámetro que usa Amazon para las búsquedas
        "search_selector": "[data-component-type='s-search-result']",  # Selector CSS para los productos en Amazon
        "link_selector": "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal"  # Selector para los enlaces de los productos en Amazon
    },
    {
        "name": "eBay",
        "search_url": "https://www.ebay.com/sch/i.html",
        "query_param": "_nkw",  # Parámetro que usa eBay para las búsquedas
        "search_selector": ".s-item",
        "link_selector": "a.s-item__link"
    },
    {
        "name": "MercadoLibre Mexico",
        "search_url": "https://listado.mercadolibre.com.mx/",
        "query_param": "q",  # Parámetro que usa MercadoLibre para las búsquedas
        "search_selector": "li.ui-search-layout__item",  # Selector CSS para los productos en MercadoLibre
        "link_selector": "a.ui-search-link__title-card"  # Selector CSS para los enlaces de los productos en MercadoLibre
    }

]

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/112.0.0.0 (Edition std-1)',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/'
        }

@main_routes.route('/buscar-productos', methods=['POST'])
def buscar_productos():
    data = request.json
    product_name = data.get('product_name')

    resultados = {}

    # Recorrer cada tienda
    for store in STORES:
        # Obtener la URL de búsqueda correcta para cada tienda
        search_url = get_search_url(store['search_url'], store['query_param'], product_name, headers)
        
        if search_url:
            # Obtener enlaces de productos
            product_links = get_product_links(search_url, store['search_selector'], store['link_selector'], headers)
            
            clean_product_links = [clean_url(link,headers) for link in product_links]

            # Agregar los enlaces de productos al resultado
            resultados[store['name']] = clean_product_links

    return jsonify(resultados)


@main_routes.route('/buscar-mejores-10', methods=['POST'])
def buscar_mejores_10():
    data = request.json
    product_name = data.get('product_name')

    productos = []

    # Recorrer cada tienda
    for store in STORES:
        search_url = get_search_url(store['search_url'], store['query_param'], product_name, headers)
        
        if search_url:
            # Obtener enlaces de productos
            product_links = get_product_links(search_url, store['search_selector'], store['link_selector'], headers)
            
            # Obtener los detalles de cada producto de los enlaces
            for link in product_links:
                producto = obtener_datos_producto(link, store['name'],headers)
                if producto:
                    productos.append(producto)

    # Ordenar los productos por precio y seleccionar los 10 mejores
    mejores_10_productos = ordenar_por_precio(productos)[:10]

    # Convertir los productos a un formato JSON para la respuesta
    mejores_10_json = [producto_to_json(p) for p in mejores_10_productos]

    return jsonify(mejores_10_json)

