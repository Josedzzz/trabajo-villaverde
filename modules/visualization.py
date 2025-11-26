"""
Modulo para analisis grafico - Villa Verde
Requerimiento iii: Analisis grafico y exploracion de tendencias
"""

import matplotlib.pyplot as plt
import pandas as pd
import os

def generar_graficas_patrones(datos_organizados, limites):
    """
    Genera graficas para identificar patrones espaciales y temporales
    
    Args:
        datos_organizados: Diccionario con datos organizados
        limites: DataFrame con limites maximos permisibles
    """
    # Crear directorio para graficas si no existe
    os.makedirs('results/graficas', exist_ok=True)
    
    datos_todos = datos_organizados['Todos']
    
    # Variables clave segun sugerencia del PDF
    variables_clave = ['Turb_NTU', 'DBO5_mgL', 'Coli_fec_NMP100mL']
    
    print("Generando graficas para variables clave:")
    print(f"  - {variables_clave}")
    
    # 1. GRAFICAS DE PATRONES ESPACIALES (entre puntos P1-P8)
    print("\n--- GENERANDO GRAFICAS DE PATRONES ESPACIALES ---")
    for variable in variables_clave:
        if variable in datos_todos.columns:
            generar_grafica_espacial(datos_todos, variable, limites)
    
    # 2. GRAFICAS DE PATRONES TEMPORALES (entre campañas C1-C4)
    print("\n--- GENERANDO GRAFICAS DE PATRONES TEMPORALES ---")
    for variable in variables_clave:
        if variable in datos_todos.columns:
            generar_grafica_temporal(datos_todos, variable, limites)
    
    # 3. GRAFICAS COMPARATIVAS DE PUNTOS CLAVE
    print("\n--- GENERANDO GRAFICAS COMPARATIVAS ---")
    puntos_comparar = ['P3', 'P4', 'P7', 'P1', 'P8']  # Segun sugerencia del PDF
    for variable in variables_clave:
        if variable in datos_todos.columns:
            generar_comparacion_puntos_clave(datos_todos, variable, puntos_comparar, limites)
    
    # 4. GRAFICAS ADICIONALES: Boxplots por campaña
    print("\n--- GENERANDO BOXPLOTS ---")
    for variable in variables_clave:
        if variable in datos_todos.columns:
            generar_boxplot_campanas(datos_todos, variable, limites)
    
    print("\n" + "="*60)
    print("ANALISIS GRAFICO COMPLETADO")
    print("="*60)
    print(f"Graficas guardadas en: results/graficas/")

def generar_grafica_espacial(datos, variable, limites):
    """
    Genera grafica de patrones espaciales entre puntos P1-P8
    """
    print(f"  - Patron espacial: {variable}")
    
    plt.figure(figsize=(12, 6))
    
    # Colores por tipo de sistema
    colores = {
        'Rio': 'blue',
        'Potable': 'green', 
        'Residual': 'red'
    }
    
    # Graficar cada punto con su color correspondiente
    for punto in sorted(datos['Punto'].unique()):
        datos_punto = datos[datos['Punto'] == punto]
        tipo_sistema = datos_punto['TipoSistema'].iloc[0]
        color = colores.get(tipo_sistema, 'gray')
        
        # Calcular promedio y desviacion por punto
        valores = datos_punto[variable].dropna()
        if len(valores) > 0:
            promedio = valores.mean()
            desviacion = valores.std()
            
            # Graficar punto con barras de error
            x_pos = list(datos['Punto'].unique()).index(punto)
            plt.errorbar(x_pos, promedio, yerr=desviacion, 
                        fmt='o', color=color, markersize=8, capsize=5,
                        label=f'P{punto} ({tipo_sistema})' if x_pos == 0 else "")
    
    # Agregar linea de LMP si existe
    lmp_info = obtener_lmp_variable(variable, limites)
    if lmp_info:
        lmp_valor = lmp_info['valor']
        if lmp_info['tipo'] == 'maximo':
            plt.axhline(y=lmp_valor, color='red', linestyle='--', linewidth=2, 
                       label=f'LMP Max: {lmp_valor} {obtener_unidades(variable)}')
        elif lmp_info['tipo'] == 'minimo':
            plt.axhline(y=lmp_valor, color='blue', linestyle='--', linewidth=2,
                       label=f'LMP Min: {lmp_valor} {obtener_unidades(variable)}')
    
    plt.title(f'Patron Espacial - {variable}\nComparacion entre puntos de muestreo')
    plt.xlabel('Puntos de Muestreo')
    plt.ylabel(f'{variable} ({obtener_unidades(variable)})')
    plt.xticks(range(len(datos['Punto'].unique())), sorted(datos['Punto'].unique()))
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Ajustar escala Y si es necesario (especialmente para coliformes)
    if 'Coli' in variable:
        plt.yscale('log')
        plt.ylabel(f'{variable} ({obtener_unidades(variable)}) - Escala Log')
    
    plt.tight_layout()
    plt.savefig(f'results/graficas/Espacial_{variable}.png', dpi=300, bbox_inches='tight')
    plt.close()

def generar_grafica_temporal(datos, variable, limites):
    """
    Genera grafica de patrones temporales a lo largo de campañas C1-C4
    """
    print(f"  - Patron temporal: {variable}")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    # Puntos clave para comparar (segun PDF)
    puntos_clave = ['P3', 'P7', 'P1', 'P8']
    colores = {'P3': 'green', 'P7': 'red', 'P1': 'blue', 'P8': 'orange'}
    
    campanas = sorted(datos['Campaña'].unique())
    
    for i, campana in enumerate(campanas):
        datos_campana = datos[datos['Campaña'] == campana]
        
        for punto in puntos_clave:
            if punto in datos_campana['Punto'].values:
                datos_punto = datos_campana[datos_campana['Punto'] == punto]
                valor = datos_punto[variable].values[0] if not datos_punto[variable].isna().all() else 0
                
                axes[i].bar(punto, valor, color=colores[punto], alpha=0.7, 
                           label=punto if i == 0 else "")
        
        axes[i].set_title(f'Campaña {campana}')
        axes[i].set_ylabel(f'{variable} ({obtener_unidades(variable)})')
        axes[i].grid(True, alpha=0.3)
        
        # Agregar LMP si existe
        lmp_info = obtener_lmp_variable(variable, limites)
        if lmp_info:
            lmp_valor = lmp_info['valor']
            if lmp_info['tipo'] == 'maximo':
                axes[i].axhline(y=lmp_valor, color='red', linestyle='--', linewidth=1)
    
    # Leyenda general
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.05), ncol=4)
    
    plt.suptitle(f'Patron Temporal - {variable}\nEvolucion por Campañas', fontsize=16)
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)
    plt.savefig(f'results/graficas/Temporal_{variable}.png', dpi=300, bbox_inches='tight')
    plt.close()

def generar_comparacion_puntos_clave(datos, variable, puntos, limites):
    """
    Genera grafica comparativa de puntos clave segun sugerencia del PDF
    Punto agua potable (P3/P4), punto residual (P7), rio aguas arriba/abajo (P1/P8)
    """
    print(f"  - Comparacion puntos clave: {variable}")
    
    plt.figure(figsize=(10, 6))
    
    # Colores y estilos
    colores = {'P3': 'green', 'P4': 'lightgreen', 'P7': 'red', 
               'P1': 'blue', 'P8': 'orange'}
    campanas = ['C1', 'C2', 'C3', 'C4']
    
    for punto in puntos:
        if punto in datos['Punto'].values:
            datos_punto = datos[datos['Punto'] == punto]
            valores = []
            
            for campana in campanas:
                valor_campana = datos_punto[datos_punto['Campaña'] == campana][variable]
                if not valor_campana.empty and not pd.isna(valor_campana.iloc[0]):
                    valores.append(valor_campana.iloc[0])
                else:
                    valores.append(0)  # O podria ser NaN
            
            plt.plot(campanas, valores, marker='o', linewidth=2.5, 
                    color=colores[punto], label=f'Punto {punto}', markersize=8)
    
    # Agregar LMP si existe
    lmp_info = obtener_lmp_variable(variable, limites)
    if lmp_info:
        lmp_valor = lmp_info['valor']
        if lmp_info['tipo'] == 'maximo':
            plt.axhline(y=lmp_valor, color='red', linestyle='--', linewidth=2,
                       label=f'LMP Max: {lmp_valor} {obtener_unidades(variable)}')
    
    plt.title(f'Comparacion de {variable} - Puntos Clave\n(Potable: P3/P4, Residual: P7, Rio: P1/P8)')
    plt.xlabel('Campaña')
    plt.ylabel(f'{variable} ({obtener_unidades(variable)})')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Escala log para coliformes
    if 'Coli' in variable:
        plt.yscale('log')
        plt.ylabel(f'{variable} ({obtener_unidades(variable)}) - Escala Log')
    
    plt.tight_layout()
    plt.savefig(f'results/graficas/Comparacion_{variable}.png', dpi=300, bbox_inches='tight')
    plt.close()

def generar_boxplot_campanas(datos, variable, limites):
    """
    Genera boxplot por campaña para ver distribucion
    """
    print(f"  - Boxplot: {variable}")
    
    plt.figure(figsize=(10, 6))
    
    # Preparar datos para boxplot
    datos_boxplot = []
    campanas = sorted(datos['Campaña'].unique())
    
    for campana in campanas:
        datos_campana = datos[datos['Campaña'] == campana][variable].dropna()
        datos_boxplot.append(datos_campana)
    
    # Crear boxplot
    plt.boxplot(datos_boxplot)
    plt.xticks(range(1, len(campanas) + 1), campanas)
    
    # Agregar LMP si existe
    lmp_info = obtener_lmp_variable(variable, limites)
    if lmp_info:
        lmp_valor = lmp_info['valor']
        if lmp_info['tipo'] == 'maximo':
            plt.axhline(y=lmp_valor, color='red', linestyle='--', linewidth=2,
                       label=f'LMP Max: {lmp_valor}')
    
    plt.title(f'Distribucion de {variable} por Campaña')
    plt.xlabel('Campaña')
    plt.ylabel(f'{variable} ({obtener_unidades(variable)})')
    plt.grid(True, alpha=0.3)
    
    if lmp_info:
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(f'results/graficas/Boxplot_{variable}.png', dpi=300, bbox_inches='tight')
    plt.close()

def obtener_lmp_variable(variable, limites):
    """
    Obtiene informacion de LMP para una variable especifica
    """
    if limites is None or limites.empty:
        return None
    
    # Mapeo de nombres de variables
    mapeo_variables = {
        'Turb_NTU': 'Turb_NTU',
        'DBO5_mgL': 'DBO5_mgL', 
        'Coli_fec_NMP100mL': 'Coli_fec_NMP100mL',
        'pH': 'pH',
        'OD_mgL': 'OD_mgL'
    }
    
    variable_buscar = mapeo_variables.get(variable, variable)
    
    fila_limite = limites[limites['Variable'] == variable_buscar]
    
    if not fila_limite.empty:
        lmp_min = fila_limite['LMP_min'].iloc[0]
        lmp_max = fila_limite['LMP_max'].iloc[0]
        
        if pd.isnull(lmp_min) and not pd.isnull(lmp_max):
            return {'valor': lmp_max, 'tipo': 'maximo'}
        elif pd.isnull(lmp_max) and not pd.isnull(lmp_min):
            return {'valor': lmp_min, 'tipo': 'minimo'}
        elif not pd.isnull(lmp_min) and not pd.isnull(lmp_max):
            return {'valor': lmp_max, 'tipo': 'maximo'}  # Para simplificar, usamos max
    
    return None

def obtener_unidades(variable):
    """
    Retorna las unidades de cada variable
    """
    unidades = {
        'Turb_NTU': 'NTU',
        'DBO5_mgL': 'mg/L',
        'Coli_fec_NMP100mL': 'NMP/100mL',
        'pH': 'unidades',
        'OD_mgL': 'mg/L',
        'Temp_C': '°C',
        'Cond_uScm': 'µS/cm',
        'Color_PtCo': 'Pt-Co',
        'Coli_tot_NMP100mL': 'NMP/100mL',
        'DQO_mgL': 'mg/L',
        'SST_mgL': 'mg/L',
        'Ntot_mgL': 'mg/L',
        'Ptot_mgL': 'mg/L',
        'Caudal_Ls': 'L/s',
        'Precip_mm_d': 'mm/dia'
    }
    return unidades.get(variable, '')
