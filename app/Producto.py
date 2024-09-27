class Producto:
    def __init__(self, nombre, precio, link, imagen, caracteristicas):
        self.nombre = nombre
        self.precio = precio
        self.link = link
        self.imagen = imagen
        self.caracteristicas = caracteristicas

    def __repr__(self):
        return f"{self.nombre} - {self.precio} - {self.link}"
