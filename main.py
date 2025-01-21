import tkinter as tk
from tkinter import simpledialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matriz de Adyacencia - Grafo Interactivo")

        # Inicializar atributos
        self.adj_matrix = [
            [0, 85, 175, 200, 50, 100],
            [85, 0, 125, 175, 100, 160],
            [175, 125, 0, 100, 200, 250],
            [200, 175, 100, 0, 210, 220],
            [50, 100, 200, 210, 0, 100],
            [100, 160, 250, 220, 100, 0]
        ]
        self.graph = nx.Graph()
        self.color_map = []  # Mapa de colores

        # Crear widgets (incluye canvas)
        self.create_widgets()

        # Actualizar grafo inicial y colorearlo
        self.update_graph()

    def update_graph(self):
        """Actualizar el grafo basado en la matriz de adyacencia y colorearlo."""
        self.graph.clear()
        n = len(self.adj_matrix)
        for i in range(n):
            for j in range(i + 1, n):
                weight = self.adj_matrix[i][j]
                if weight > 0 and weight < 150:  # Conectar nodos solo si el peso < 150
                    self.graph.add_edge(i + 1, j + 1, weight=weight)

        # Colorear automáticamente después de actualizar el grafo
        self.color_graph()

    def draw_graph(self):
        """Dibujar el grafo en la interfaz."""
        plt.clf()
        pos = nx.spring_layout(self.graph)
        weights = nx.get_edge_attributes(self.graph, 'weight')

        nx.draw(self.graph, pos, with_labels=True, node_color=self.color_map or 'skyblue', 
                node_size=500, font_weight='bold')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=weights)
        self.canvas.draw()

    def add_node(self):
        """Agregar un nodo al grafo con valores de caminos hacia otros nodos."""
        n = len(self.adj_matrix)
        new_row = []
        for i in range(n):
            value = simpledialog.askinteger("Agregar Camino", f"Peso del camino de nodo {n+1} a nodo {i+1}:",
                                            parent=self.root, minvalue=0, initialvalue=0)
            if value is None:  # Cancelar
                return
            new_row.append(value)
        
        # Agregar el nuevo nodo a la matriz
        for i, row in enumerate(self.adj_matrix):
            row.append(new_row[i])
        new_row.append(0)  # El nodo a sí mismo tiene peso 0
        self.adj_matrix.append(new_row)

        self.update_graph()

    def remove_node(self):
        """Eliminar un nodo del grafo."""
        if len(self.adj_matrix) > 1:
            self.adj_matrix.pop()
            for row in self.adj_matrix:
                row.pop()
            self.update_graph()
        else:
            messagebox.showwarning("Advertencia", "No se pueden eliminar más nodos.")

    def dsatur_coloring(self, grafo):
        """Colorear el grafo utilizando el algoritmo DSatur."""
        nodes = list(grafo.nodes())
        degrees = {node: len(list(grafo.neighbors(node))) for node in nodes}
        saturation = {node: 0 for node in nodes}
        color_assignment = {}

        while len(color_assignment) < len(nodes):
            # Seleccionar nodo con mayor saturación; si hay empate, elegir el de mayor grado
            node_to_color = max(
                (node for node in nodes if node not in color_assignment),
                key=lambda node: (saturation[node], degrees[node])
            )

            # Encontrar colores válidos
            neighbor_colors = {color_assignment[neighbor] for neighbor in grafo.neighbors(node_to_color) if neighbor in color_assignment}
            color = next(c for c in range(len(nodes)) if c not in neighbor_colors)

            # Asignar color
            color_assignment[node_to_color] = color

            # Actualizar saturación de los vecinos
            for neighbor in grafo.neighbors(node_to_color):
                if neighbor not in color_assignment:
                    saturation[neighbor] = len({color_assignment[n] for n in grafo.neighbors(neighbor) if n in color_assignment})

        return color_assignment

    def color_graph(self):
        """Colorear el grafo usando DSatur y actualizar los colores en la interfaz."""
        coloreado = self.dsatur_coloring(self.graph)

        # Generar el mapa de colores
        colores = ['lightblue', 'orange', 'lightgreen', 'pink', 'yellow', 'purple', 'red', 'cyan']
        self.color_map = [colores[coloreado[nodo] % len(colores)] for nodo in self.graph.nodes()]
        self.draw_graph()

    def match_nodes(self):
        """Emparejar nodos cuya distancia sea menor a 150."""
        matching = nx.max_weight_matching(self.graph, maxcardinality=True)
        matched_edges = [(u, v) for u, v in matching if self.graph[u][v]['weight'] < 150]
        
        # Dibujar el emparejamiento en el grafo
        plt.clf()
        pos = nx.spring_layout(self.graph)
        weights = nx.get_edge_attributes(self.graph, 'weight')

        nx.draw(self.graph, pos, with_labels=True, node_color=self.color_map or 'skyblue', 
                node_size=500, font_weight='bold')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=weights)
        nx.draw_networkx_edges(self.graph, pos, edgelist=matched_edges, edge_color='r', width=2)
        self.canvas.draw()

    def create_widgets(self):
        """Crear los widgets de la interfaz gráfica."""
        # Figura de matplotlib
        self.figure = plt.figure(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Botones
        btn_add = tk.Button(self.root, text="Agregar Nodo", command=self.add_node)
        btn_add.pack(side=tk.LEFT, padx=10, pady=10)

        btn_remove = tk.Button(self.root, text="Eliminar Nodo", command=self.remove_node)
        btn_remove.pack(side=tk.LEFT, padx=10, pady=10)

        btn_match = tk.Button(self.root, text="Emparejar Nodos", command=self.match_nodes)
        btn_match.pack(side=tk.LEFT, padx=10, pady=10)

# Crear la aplicación
root = tk.Tk()
app = GraphApp(root)
root.mainloop()
