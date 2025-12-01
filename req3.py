"""
REQUERIMIENTO 3: ANALISIS GRAFICO
Variables del grupo: Turbiedad, Color aparente, Coliformes totales, Coliformes fecales, Caudal, Precipitacion
"""

import pandas as pd
import matplotlib.pyplot as plt

print("=== REQUERIMIENTO 3: ANALISIS GRAFICO ===\n")

print("Cargando datos...")

# Cargar datos directamente
datos = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Datos')
coordenadas = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Coordenadas')
limites = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Limites')

# Variables de nuestro grupo
variables_grupo = ['Turb_NTU', 'Color_PtCo', 'Coli_tot_NMP100mL', 'Coli_fec_NMP100mL', 'Caudal_Ls', 'Precip_mm_d']
columnas_mantener = ['Punto', 'TipoSistema', 'Campaña'] + variables_grupo

datos_filtrados = datos[columnas_mantener].copy()
datos_completos = datos_filtrados.merge(coordenadas[['Punto', 'Descripcion']], on='Punto', how='left')

print("Generando graficas...")

# Variables clave para graficar (3 como minimo)
variables_clave = ['Turb_NTU', 'Coli_fec_NMP100mL', 'Caudal_Ls']

# 1. Graficas de patrones espaciales (entre TODOS los puntos P1-P8)
print("\n1. Generando graficas de patrones espaciales (todos los puntos)...")

for variable in variables_clave:
    plt.figure(figsize=(14, 6))
    
    # Colores por tipo de sistema
    colores = {'Rio': 'blue', 'Potable': 'green', 'Residual': 'red'}
    
    # Calcular promedio por punto manualmente para TODOS los puntos
    puntos = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']
    promedios = []
    tipos = []
    desviaciones = []
    
    for punto in puntos:
        datos_punto = datos_completos[datos_completos['Punto'] == punto]
        if len(datos_punto) > 0:
            # Calcular promedio y desviacion manual
            valores = []
            for i in range(len(datos_punto)):
                valor = datos_punto.iloc[i][variable]
                if valor == valor:  # Filtrar NaN
                    valores.append(valor)
            
            if valores:
                promedio = sum(valores) / len(valores)
                # Calcular desviacion estandar
                suma_cuadrados = sum((x - promedio) ** 2 for x in valores)
                desviacion = (suma_cuadrados / len(valores)) ** 0.5
                
                promedios.append(promedio)
                desviaciones.append(desviacion)
                tipos.append(datos_punto.iloc[0]['TipoSistema'])
            else:
                promedios.append(0)
                desviaciones.append(0)
                tipos.append('Desconocido')
        else:
            promedios.append(0)
            desviaciones.append(0)
            tipos.append('Desconocido')
    
    # Graficar con barras de error
    for i, punto in enumerate(puntos):
        color = colores.get(tipos[i], 'gray')
        plt.bar(punto, promedios[i], color=color, alpha=0.7, 
                yerr=desviaciones[i], capsize=5,
                label=f'{tipos[i]}' if i == puntos.index('P1') or i == puntos.index('P3') or i == puntos.index('P5') else "")
    
    plt.title(f'Patron Espacial - {variable}\nComparacion entre TODOS los puntos de muestreo')
    plt.xlabel('Puntos de Muestreo')
    
    # Agregar unidades
    unidades = {'Turb_NTU': 'NTU', 'Coli_fec_NMP100mL': 'NMP/100mL', 'Caudal_Ls': 'L/s'}
    plt.ylabel(f'{variable} ({unidades.get(variable, "")})')
    
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f'results/graficas/espacial_todos_{variable}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Grafica guardada: espacial_todos_{variable}.png")

# 2. Graficas de patrones temporales (entre campañas C1-C4 para TODOS los puntos)
print("\n2. Generando graficas de patrones temporales (todos los puntos)...")

for variable in variables_clave:
    plt.figure(figsize=(14, 8))
    
    # TODOS los puntos P1-P8
    todos_puntos = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']
    colores = {'P1': 'blue', 'P2': 'lightblue', 'P3': 'green', 'P4': 'lightgreen',
               'P5': 'red', 'P6': 'pink', 'P7': 'orange', 'P8': 'yellow'}
    
    for punto in todos_puntos:
        datos_punto = datos_completos[datos_completos['Punto'] == punto]
        if len(datos_punto) > 0:
            # Recolectar valores por campaña manualmente
            campanas = ['C1', 'C2', 'C3', 'C4']
            valores_campanas = []
            
            for campana in campanas:
                valor_encontrado = None
                for i in range(len(datos_punto)):
                    if datos_punto.iloc[i]['Campaña'] == campana:
                        valor = datos_punto.iloc[i][variable]
                        if valor == valor:  # Filtrar NaN
                            valor_encontrado = valor
                            break
                valores_campanas.append(valor_encontrado if valor_encontrado is not None else None)
            
            # Graficar solo si hay datos
            if any(v is not None for v in valores_campanas):
                plt.plot(campanas, valores_campanas, marker='o', label=f'P{punto}', 
                        color=colores[punto], linewidth=2, markersize=6)
    
    plt.title(f'Patron Temporal - {variable}\nEvolucion por Campañas - TODOS los puntos')
    plt.xlabel('Campaña')
    unidades = {'Turb_NTU': 'NTU', 'Coli_fec_NMP100mL': 'NMP/100mL', 'Caudal_Ls': 'L/s'}
    plt.ylabel(f'{variable} ({unidades.get(variable, "")})')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'results/graficas/temporal_todos_{variable}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Grafica guardada: temporal_todos_{variable}.png")

# 3. Graficas comparativas de puntos clave (P3, P7, P1, P8) + todos los puntos
print("\n3. Generando graficas comparativas...")

for variable in variables_clave:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Subgrafica 1: Puntos clave segun PDF
    puntos_clave = ['P3', 'P7', 'P1', 'P8']
    colores_clave = {'P3': 'green', 'P7': 'red', 'P1': 'blue', 'P8': 'orange'}
    
    for punto in puntos_clave:
        datos_punto = datos_completos[datos_completos['Punto'] == punto]
        if len(datos_punto) > 0:
            campanas = ['C1', 'C2', 'C3', 'C4']
            valores_campanas = []
            
            for campana in campanas:
                valor_encontrado = None
                for i in range(len(datos_punto)):
                    if datos_punto.iloc[i]['Campaña'] == campana:
                        valor = datos_punto.iloc[i][variable]
                        if valor == valor:
                            valor_encontrado = valor
                            break
                valores_campanas.append(valor_encontrado if valor_encontrado is not None else 0)
            
            ax1.plot(campanas, valores_campanas, marker='s', label=f'P{punto}', 
                    color=colores_clave[punto], linewidth=2.5, markersize=8)
    
    ax1.set_title(f'Puntos Clave - {variable}')
    ax1.set_xlabel('Campaña')
    unidades = {'Turb_NTU': 'NTU', 'Coli_fec_NMP100mL': 'NMP/100mL', 'Caudal_Ls': 'L/s'}
    ax1.set_ylabel(f'{variable} ({unidades.get(variable, "")})')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Subgrafica 2: Todos los puntos
    todos_puntos = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']
    colores_todos = {'P1': 'blue', 'P2': 'lightblue', 'P3': 'green', 'P4': 'lightgreen',
                    'P5': 'red', 'P6': 'pink', 'P7': 'orange', 'P8': 'yellow'}
    
    for punto in todos_puntos:
        datos_punto = datos_completos[datos_completos['Punto'] == punto]
        if len(datos_punto) > 0:
            # Calcular promedio del punto
            valores = []
            for i in range(len(datos_punto)):
                valor = datos_punto.iloc[i][variable]
                if valor == valor:
                    valores.append(valor)
            
            if valores:
                promedio = sum(valores) / len(valores)
                ax2.bar(punto, promedio, color=colores_todos[punto], alpha=0.7)
    
    ax2.set_title(f'Todos los Puntos - {variable}')
    ax2.set_xlabel('Puntos de Muestreo')
    ax2.set_ylabel(f'{variable} ({unidades.get(variable, "")})')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'results/graficas/comparativa_{variable}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Grafica guardada: comparativa_{variable}.png")

# 4. Boxplots por campaña - FORMA MANUAL
print("\n4. Generando boxplots por campaña...")

for variable in variables_clave:
    plt.figure(figsize=(10, 6))
    
    # Preparar datos para boxplot manualmente
    datos_por_campana = {campana: [] for campana in ['C1', 'C2', 'C3', 'C4']}
    
    for i in range(len(datos_completos)):
        campana = datos_completos.iloc[i]['Campaña']
        valor = datos_completos.iloc[i][variable]
        if valor == valor:  # Filtrar NaN
            datos_por_campana[campana].append(valor)
    
    # Crear boxplot manual con matplotlib
    campanas = ['C1', 'C2', 'C3', 'C4']
    datos_boxplot = [datos_por_campana[campana] for campana in campanas]
    
    # Crear boxplot sin usar pandas
    plt.boxplot(datos_boxplot)
    plt.xticks([1, 2, 3, 4], campanas)  # Posiciones 1,2,3,4 con labels C1,C2,C3,C4
    
    plt.title(f'Distribucion de {variable} por Campaña')
    unidades = {'Turb_NTU': 'NTU', 'Coli_fec_NMP100mL': 'NMP/100mL', 'Caudal_Ls': 'L/s'}
    plt.ylabel(f'{variable} ({unidades.get(variable, "")})')
    plt.xlabel('Campaña')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'results/graficas/boxplot_{variable}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Grafica guardada: boxplot_{variable}.png")

print(f"\nREQUERIMIENTO 3 COMPLETADO")
print(f"{len(variables_clave) * 4} graficas guardadas en 'results/graficas/'")
