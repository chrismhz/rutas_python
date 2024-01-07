from flask import Flask, request, jsonify, render_template
import math
from operator import itemgetter

app = Flask(__name__)

# Coordenadas predefinidas
coord = {
    'JiloYork': (19.984146, -99.519127),
    'Toluca': (19.286167856525594, -99.65473296644892),
    'Atlacomulco': (19.796802401380955, -99.87643301629244),
    'Guadalajara': (20.655773344775373, -103.35773871581326),
    'Monterrey': (25.675859554333684, -100.31405053526082),
    'Cancun': (21.158135651777727, -86.85092947858692),
    'Morelia': (19.720961251258654, -101.15929186858635),
    'Aguascalientes': (21.88473831747085, -102.29198705069501),
    'Queretaro': (20.57005870003398, -100.45222862892079),
    'CDMX': (19.429550164848152, -99.13000959477478)
}

def distancia(coord1, coord2):
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def en_ruta(rutas, c):
    ruta = None
    for rutas in rutas:
        if c in rutas:
            ruta = rutas
    return ruta

def peso_ruta(ruta, pedidos):
    total = 0
    for c in ruta:
        total = total + pedidos[c]
    return total

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular_rutas', methods=['POST'])
def calcular_rutas():
    data = request.get_json()
    pedidos = data['pedidos']
    max_carga = data['max_carga']
    
    # Define el almacén directamente aquí
    almacen = (19.814895, -99.521053)
    
    # Calcular las rutas
    s = {}
    for c1 in coord:
        for c2 in coord:
            if c1 != c2:
                if not (c2, c1) in s:
                    d_c1_c2 = distancia(coord[c1], coord[c2])
                    d_c1_almacen = distancia(coord[c1], almacen)
                    d_c2_almacen = distancia(coord[c2], almacen)
                    s[c1, c2] = d_c1_almacen + d_c2_almacen - d_c1_c2

    s = sorted(s.items(), key=itemgetter(1), reverse=True)

    rutas = []
    for k, v in s:
        rc1 = en_ruta(rutas, k[0])
        rc2 = en_ruta(rutas, k[1])
        if rc1 == None and rc2 == None:
            if pedidos[k[0]] > 0 and pedidos[k[1]] > 0 and peso_ruta([k[0], k[1]], pedidos) <= max_carga:
                rutas.append([k[0], k[1]])
        elif rc1 != None and rc2 == None:
            if rc1[0] == k[0]:
                if pedidos[k[1]] > 0 and peso_ruta(rc1, pedidos) + pedidos[k[1]] <= max_carga:
                    rutas[rutas.index(rc1)].insert(0, k[1])
            elif rc1[len(rc1) - 1] == k[0]:
                if pedidos[k[1]] > 0 and peso_ruta(rc1, pedidos) + pedidos[k[1]] <= max_carga:
                    rutas[rutas.index(rc1)].append(k[1])
        elif rc1 == None and rc2 != None:
            if rc2[0] == k[1]:
                if pedidos[k[0]] > 0 and peso_ruta(rc2, pedidos) + pedidos[k[0]] <= max_carga:
                    rutas[rutas.index(rc2)].insert(0, k[0])
            elif rc2[len(rc2) - 1] == k[1]:
                if pedidos[k[0]] > 0 and peso_ruta(rc2, pedidos) + pedidos[k[0]] <= max_carga:
                    rutas[rutas.index(rc2)].append(k[0])
        elif rc1 != None and rc2 != None and rc1 != rc2:
            if rc1[0] == k[0] and rc2[len(rc2) - 1] == k[1]:
                if pedidos[k[0]] > 0 and pedidos[k[1]] > 0 and peso_ruta(rc1, pedidos) + peso_ruta(rc2, pedidos) <= max_carga:
                    rutas[rutas.index(rc2)].extend(rc1)
                    rutas.remove(rc1)
            elif rc1[len(rc1) - 1] == k[0] and rc2[0] == k[1]:
                if pedidos[k[0]] > 0 and pedidos[k[1]] > 0 and peso_ruta(rc1, pedidos) + peso_ruta(rc2, pedidos) <= max_carga:
                    rutas[rutas.index(rc1)].extend(rc2)
                    rutas.remove(rc2)
    
    return jsonify({'rutas': rutas})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
