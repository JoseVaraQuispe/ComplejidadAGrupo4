import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image, ImageFilter
import csv
from tkinter import ttk
import sys
import heapq
import datetime
import matplotlib.pyplot as plt
import networkx as nx
import random
from functools import partial


def load_movies_data(file_path):
    movies_data = {}

    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            title = row[0]
            rating = float(row[1])
            genre = row[2]
            year = int(row[3])
            image_path = row[5]
            movies_data[title] = {'title': title, 'rating': rating, 'genre': genre, 'year': year, 'image_path': image_path}

    return movies_data


def build_movie_graph(movies_data):
    G = nx.Graph()

    for movie, data in movies_data.items():
        G.add_node(movie, title=movie, rating=data['rating'], genre=data['genre'], year=data['year'], image_path=data['image_path'])

    for movie1, data1 in movies_data.items():
        for movie2, data2 in movies_data.items():
            if movie1 != movie2:
                genre_similarity = 1 if data1['genre'] == data2['genre'] else 0
                rating_difference = abs(data1['rating'] - data2['rating'])
                year_difference = abs(data1['year'] - data2['year'])
                days_since_release = (datetime.datetime.now().year - data2['year']) * 365
                weight = genre_similarity + rating_difference + year_difference + (days_since_release / 365)
                G.add_edge(movie1, movie2, weight=weight)

    return G


def dijkstra_movie_recommendations(G, start_movie, año=None, max_recommendations=5):
    shortest_paths = nx.shortest_path_length(G, source=start_movie, weight='weight')
    recommendations = []

    for movie, distance in shortest_paths.items():
        if año is not None and movies_data[movie]['year'] != int(año):
            continue
        recommendations.append((movie, distance))

    recommendations = heapq.nsmallest(max_recommendations, recommendations, key=lambda x: x[1])

    return recommendations

def mostrar_resultados(resultados, mostrar_grafo_func):
    ventana_resultados = tk.Toplevel(ventana)
    ventana_resultados.title("Resultados de la búsqueda")

    if not resultados:
        mensaje_label = tk.Label(ventana_resultados, text="No se encontraron resultados")
        mensaje_label.pack(padx=20, pady=20)
    else:
        marco_fila = None
        contador = 0

        for i, (movie, distance) in enumerate(resultados):
            titulo = movies_data[movie]['title']
            genero = movies_data[movie]['genre']
            año = movies_data[movie]['year']
            imagen_ruta = movies_data[movie]['image_path']
            imagen = Image.open(imagen_ruta)
            imagen = imagen.resize((100, 150), Image.LANCZOS)
            imagen = ImageTk.PhotoImage(imagen)

            if i % 5 == 0:
                marco_fila = tk.Frame(ventana_resultados)
                marco_fila.pack(pady=10)

            marco_pelicula = tk.Frame(marco_fila)
            marco_pelicula.pack(side="left", padx=10)

            imagen_label = tk.Label(marco_pelicula, image=imagen)
            imagen_label.image = imagen
            imagen_label.pack()

            titulo_label = tk.Label(marco_pelicula, text=titulo)
            titulo_label.pack()

            genero_label = tk.Label(marco_pelicula, text="Género: " + genero)
            genero_label.pack()

            año_label = tk.Label(marco_pelicula, text="Año: " + str(año))
            año_label.pack()

            contador += 1

            if contador == 5:
                contador = 0

        boton_mostrar_grafo = tk.Button(ventana_resultados, text="Mostrar Grafo", command=mostrar_grafo_func)
        boton_mostrar_grafo.pack(pady=10)

    ventana_resultados.mainloop()


import matplotlib.colors as mcolors

def mostrar_grafo():
    pelicula_seleccionada = combobox_peliculas.get()

    if pelicula_seleccionada:
        subgraph = nx.Graph()

        recomendaciones = dijkstra_movie_recommendations(movie_graph, pelicula_seleccionada)
        for movie, distance in recomendaciones:
            subgraph.add_node(movie, **movie_graph.nodes[movie])
            for neighbor in movie_graph.neighbors(movie):
                if neighbor in subgraph.nodes:
                    subgraph.add_edge(movie, neighbor, **movie_graph.edges[movie, neighbor])

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(subgraph, seed=42)
        labels = nx.get_node_attributes(subgraph, 'title')
        node_colors = [subgraph.nodes[node]['rating'] for node in subgraph.nodes()]
        node_sizes = [subgraph.degree(node) * 100 for node in subgraph.nodes()]
        edge_weights = [subgraph.edges[edge]['weight'] for edge in subgraph.edges()]

        edge_cmap = mcolors.ListedColormap(['b'])

        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, node_size=node_sizes, cmap='cool', alpha=0.7)
        nx.draw_networkx_edges(subgraph, pos, edge_color=edge_weights, edge_cmap=edge_cmap, width=1, alpha=0.7)
        nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=nx.get_edge_attributes(subgraph, 'weight'))

        nx.draw_networkx_labels(subgraph, pos, labels, font_size=10)

        plt.title(f'Relaciones de películas recomendadas para: {pelicula_seleccionada}')
        plt.axis('off')
        plt.show()
    else:
        messagebox.showwarning("Mostrar Grafo", "Seleccione una película para mostrar el grafo de relaciones")



def buscar_pelicula():
    termino_busqueda = entrada_busqueda.get()

    if termino_busqueda:
        resultados = []
        for titulo, datos in movies_data.items():
            if termino_busqueda.lower() in titulo.lower():
                resultados.append((titulo, datos['rating']))

        mostrar_resultados(resultados, mostrar_grafo)

    else:
        messagebox.showwarning("Búsqueda", "Ingrese un término de búsqueda")


def abrir_ventana_recomendaciones():
    global combobox_peliculas, combobox_anios

    ventana_recomendaciones = tk.Toplevel(ventana)
    ventana_recomendaciones.title("Recomendaciones")

    label_titulo = tk.Label(ventana_recomendaciones, text="Seleccione una película para obtener recomendaciones:")
    label_titulo.pack(padx=10, pady=10)

    opciones_peliculas = list(movies_data.keys())
    combobox_peliculas = ttk.Combobox(ventana_recomendaciones, values=opciones_peliculas)
    combobox_peliculas.pack(padx=10, pady=5)

    label_titulo = tk.Label(ventana_recomendaciones, text="Filtrar por año:")
    label_titulo.pack(padx=10, pady=10)
    opciones_anios = ["Sin restricción"] + list(set(movie["year"] for movie in movies_data.values()))
    combobox_anios = ttk.Combobox(ventana_recomendaciones, values=opciones_anios)
    combobox_anios.pack(padx=10, pady=5)

    mostrar_grafo_func = partial(mostrar_grafo)

    boton_obtener_recomendaciones = tk.Button(ventana_recomendaciones, text="Obtener Recomendaciones",
        command=lambda: obtener_recomendaciones(combobox_peliculas.get(), combobox_anios.get(), mostrar_grafo_func))
    boton_obtener_recomendaciones.pack(padx=10, pady=10)


def obtener_recomendaciones(pelicula, anio, mostrar_grafo_func):
    if pelicula:
        if anio == "Sin restricción":
            recomendaciones = dijkstra_movie_recommendations(movie_graph, pelicula)
            mostrar_resultados(recomendaciones, mostrar_grafo_func)
        else:
            recomendaciones = dijkstra_movie_recommendations(movie_graph, pelicula, anio)
            mostrar_resultados(recomendaciones, mostrar_grafo_func)
    else:
        messagebox.showwarning("Recomendaciones", "Seleccione una película para obtener recomendaciones")

def create_recent_movies_page(notebook, movies):
    page = ttk.Frame(notebook)

    marco_fila = None
    contador = 0

    for i, movie in enumerate(movies):
        titulo = movie
        genero = movies_data[movie]['genre']
        año = movies_data[movie]['year']
        imagen_ruta = movies_data[movie]['image_path']
        imagen = Image.open(imagen_ruta)
        imagen = imagen.resize((100, 150), Image.LANCZOS)
        imagen = ImageTk.PhotoImage(imagen)

        if i % 5 == 0:
            marco_fila = tk.Frame(page)
            marco_fila.pack(pady=10)

        marco_pelicula = tk.Frame(marco_fila)
        marco_pelicula.pack(side="left", padx=10)

        imagen_label = tk.Label(marco_pelicula, image=imagen)
        imagen_label.image = imagen
        imagen_label.pack()

        titulo_label = tk.Label(marco_pelicula, text=titulo)
        titulo_label.pack()

        genero_label = tk.Label(marco_pelicula, text="Género: " + genero)
        genero_label.pack()

        año_label = tk.Label(marco_pelicula, text="Año: " + str(año))
        año_label.pack()

        contador += 1

        if contador == 5:
            contador = 0

    return page

def abrir_ventana_integrantes():
    ventana_integrantes = tk.Toplevel(ventana)
    ventana_integrantes.title("Integrantes")

    integrantes = [
        {"nombre": "José Carlos Vara Quispe", "codigo": "U202125116", "rol": "Programador"},
        {"nombre": "Maria Laura Aragon Flores", "codigo": "U202013882", "rol": "Programador"},
        {"nombre": "Paolo Sebastian Padilla Advincula", "codigo": "U202117993", "rol": "Programador"},
    ]
    
    for i, integrante in enumerate(integrantes):
        etiqueta_nombre = tk.Label(ventana_integrantes, text="Nombre: " + integrante["nombre"])
        etiqueta_nombre.pack()
        
        etiqueta_edad = tk.Label(ventana_integrantes, text="Código: " + str(integrante["codigo"]))
        etiqueta_edad.pack()
        
        etiqueta_rol = tk.Label(ventana_integrantes, text="Rol: " + integrante["rol"])
        etiqueta_rol.pack()
        
        if i < len(integrantes) - 1:
            separador = tk.Label(ventana_integrantes, text="-------------------------")
            separador.pack()

csv_file = 'movies.csv'
movies_data = load_movies_data(csv_file)
movie_graph = build_movie_graph(movies_data)
recent_movies = random.sample(list(movies_data.keys()), 20)

ventana = tk.Tk()
ventana.title("Moviedle - Búsqueda y Recomendación de Películas")

barra_superior = tk.Frame(ventana, bg="black")
barra_superior.pack(fill=tk.X)

nombre_app = tk.Label(barra_superior, text="Moviedle", fg="white", bg="black", font=("Arial", 24, "bold"))
nombre_app.pack(padx=10, pady=5)

marco_principal = tk.Frame(ventana)
marco_principal.pack(fill=tk.BOTH, expand=True)

barra_lateral = tk.Frame(marco_principal, bg="black", width=150)
barra_lateral.pack(side=tk.LEFT, fill=tk.Y)

contenedor_busqueda = tk.Frame(marco_principal, padx=10, pady=10)
contenedor_busqueda.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

etiqueta_busqueda = tk.Label(contenedor_busqueda, text="Búsqueda de Películas")
etiqueta_busqueda.pack(padx=10, pady=5)

entrada_busqueda = tk.Entry(contenedor_busqueda, width=50)
entrada_busqueda.pack(padx=10, pady=5)

boton_buscar = tk.Button(contenedor_busqueda, text="Buscar", command=buscar_pelicula)
boton_buscar.pack(padx=5, pady=5, side=tk.RIGHT)

boton_recomendaciones = tk.Button(barra_lateral, text="Recomendaciones", bg="black", fg="white", bd=0, padx=10,
    pady=5, command=abrir_ventana_recomendaciones)
boton_recomendaciones.pack(side=tk.TOP, fill=tk.X)

boton_integrantes = tk.Button(barra_lateral, text="Integrantes", bg="black", fg="white", bd=0, padx=10,
    pady=5, command=abrir_ventana_integrantes)
boton_integrantes.pack(side=tk.TOP, fill=tk.X)

notebook = ttk.Notebook(marco_principal)
notebook.pack(fill=tk.BOTH, expand=True)

num_pages = 3  
movies_per_page = 8  

for page_num in range(num_pages):
    start_index = page_num * movies_per_page
    end_index = start_index + movies_per_page
    movies_page = list(recent_movies[start_index:end_index])
    page = create_recent_movies_page(notebook, movies_page)
    notebook.add(page, text=f"Página {page_num + 1}")

ventana.mainloop()
