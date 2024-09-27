import requests
import re
import urllib.parse
from urllib.parse import urlparse,urlunparse,urlsplit
import httpagentparser
from .Producto import Producto
from bs4 import BeautifulSoup


def clean_url(url,headers):
    # Verificar si la URL pertenece a MercadoLibre
    if 'mercadolibre.com' in url:
        # Usa una expresión regular para encontrar el patrón hasta el identificador del producto
        match = re.search(r'(.*?/p/\w+)', url)
        if match:
            # Si se encuentra un match, usa esa parte de la URL
            cleaned_url = match.group(1)
        else:
            # Si no se encuentra el patrón, retorna la URL original
            cleaned_url = url.split('%')[0]
    else:
        # Divide la URL en sus componentes
        parsed_url = urlsplit(url)
    
        # Reconstruye la URL sin el fragmento (parámetros después del '#')
        cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    
    return cleaned_url

# Función para construir la URL de búsqueda correctamente según la tienda
def get_search_url(search_url, query_param, search_term, headers):
    try:
        # Construir la URL con el parámetro de búsqueda correcto
        query = {query_param: search_term}
        search_url_with_query = f"{search_url}?{urllib.parse.urlencode(query)}"
        response = requests.get(search_url_with_query)

        # Devolver la URL final (después de redirección si es necesario)
        if response.history:
            return response.url
        return search_url_with_query

    except requests.RequestException as e:
        # En caso de error, devuelve None y registra el error
        print("Error al realizar la solicitud en la URL de busqueda")
        return None

# Función para obtener los enlaces de productos en la página de búsqueda
def get_product_links(search_url, product_selector, product_link_selector, headers):
    

    try:
        
        # Realizar la solicitud HTTP
        response = requests.get(search_url,headers=headers,timeout=10)

        if response.status_code == 200:
            # Detectar la codificación más probable
            encoding = response.apparent_encoding

            # Decodificar el contenido usando la codificación detectada
            content = response.content.decode(encoding, errors='replace')

            # Parsear el contenido con BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')

            # Buscar los elementos de productos según el selector proporcionado
            product_items = soup.select(product_selector)

            if not product_items:
                print("No se encontraron productos en la pagina de busqueda")

            product_links = []
            for product in product_items:
                try:
                    # Obtener el enlace del producto
                    link = product.select_one(product_link_selector)
                    if link and 'href' in link.attrs:
                        # Obtener el valor del atributo href
                        href = link['href']
                        # Construir el enlace completo (relativo -> absoluto)
                        full_link = requests.compat.urljoin(search_url, href)
                        # Codificar los caracteres especiales de la URL para evitar problemas
                        full_link_safe = urllib.parse.quote(full_link, safe=":/?=&")
                        product_links.append(full_link_safe)
                    else:
                        print("Elemento sin enlace")
                except Exception:
                    print("Error al obtener el enlace del producto")
                    
                    continue

            # Retornar los enlaces de productos encontrados
            return product_links

        else:
            # En caso de un código de estado HTTP que no sea exitoso
            print("Error al acceder al enlace, codigo de estado incorrecto")
            print(search_url)
            return []

    except requests.RequestException:
        # En caso de que la solicitud HTTP falle
        print("Error en la solicitud HTTP")
        return []

    except UnicodeDecodeError:
        # En caso de un error de codificación
        print("Error en la decodificacion")
        return []


def obtener_datos_producto(link, store_name,headers):

    
    try:
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            if store_name == "MercadoLibre Mexico":
                nombre = soup.find('h1', class_='ui-pdp-title').get_text(strip=True)
                precio = soup.find('span', class_='').get_text(strip=True)
                imagen = soup.find('img', class_='')['src']
                caracteristicas = [li.get_text(strip=True) for li in soup.find_all('li', class_='ui-pdp-list__item')]

            elif store_name == "Amazon Mexico":
                nombre = soup.find('span', id='').get_text(strip=True)
                precio = soup.find('span', class_='').get_text(strip=True)
                imagen = soup.find('img', id='')['src']
                caracteristicas = [li.get_text(strip=True) for li in soup.find_all('li', id='feature-bullets')]

            elif store_name == "eBay":
                nombre = soup.find('h1', class_='').get_text(strip=True)
                precio = soup.find('span', class_='').get_text(strip=True)
                imagen = soup.find('img', id='icImg')['src']
                caracteristicas = [li.get_text(strip=True) for li in soup.find_all('li', class_='itemAttr')]

            return Producto(nombre, precio, link, imagen, caracteristicas)

    except Exception as e:
        print(f"Error al obtener datos del producto en {store_name}: {e}")
    
    return None


def obtener_productos(lista_links):
    productos = []
    for link in lista_links:
        producto = obtener_datos_producto(link)
        if producto:
            productos.append(producto)
    return productos

def ordenar_por_precio(productos):
    return sorted(productos, key=lambda p: float(p.precio.replace(',', '').replace('$', '')))

def filtrar_por_caracteristica(productos, palabra_clave):
    return [p for p in productos if any(palabra_clave.lower() in c.lower() for c in p.caracteristicas)]

def producto_to_json(producto):
    return {
        'nombre': producto.nombre,
        'precio': producto.precio,
        'link': producto.link,
        'imagen': producto.imagen,
        'caracteristicas': producto.caracteristicas
    }
