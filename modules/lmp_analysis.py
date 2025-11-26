"""
Modulo para evaluacion de limites maximos permisibles - Villa Verde
Requerimiento iv: Evaluacion frente a LMP
"""

import pandas as pd
import matplotlib.pyplot as plt

def evaluar_limites_permitidos(datos_organizados, limites):
    """
    Evalua el cumplimiento de limites maximos permisibles
    
    Args:
        datos_organizados: Diccionario con datos organizados
        limites: DataFrame con limites maximos
    """
    if limites is None or limites.empty:
        print("No se pueden evaluar LMP - limites no cargados")
        return
    
    datos_todos = datos_organizados['Todos']
    
    # a. Determinar puntos y campañas que superaron LMP
    print("\n--- IDENTIFICANDO INCUMPLIMIENTOS ---")
    incumplimientos = identificar_incumplimientos(datos_todos, limites)
    
    # b. Calcular porcentajes de no cumplimiento
    print("\n--- CALCULANDO PORCENTAJES DE NO CUMPLIMIENTO ---")
    porcentajes = calcular_porcentajes_incumplimiento(datos_todos, limites)
    
    # c. Identificar puntos mas criticos por sistema
    print("\n--- IDENTIFICANDO PUNTOS MAS CRITICOS ---")
    puntos_criticos = identificar_puntos_criticos(incumplimientos)
    
    # d. Generar graficas con incumplimientos destacados
    print("\n--- GENERANDO GRAFICAS CON INCUMPLIMIENTOS ---")
    generar_graficas_incumplimientos(datos_organizados, limites, incumplimientos)
    
    # e. Exportar resultados
    print("\n--- EXPORTANDO RESULTADOS ---")
    exportar_resultados_lmp(incumplimientos, porcentajes, puntos_criticos)
    
    print("\n" + "="*60)
    print("EVALUACION LMP COMPLETADA")
    print("="*60)

def identificar_incumplimientos(datos, limites):
    """
    Identifica que puntos y campañas superaron los LMP
    """
    print("Analizando incumplimientos por variable...")
    
    incumplimientos = []
    
    for _, fila_limite in limites.iterrows():
        variable = fila_limite['Variable']
        tipo_sistema_limite = fila_limite['TipoSistema']
        lmp_min = fila_limite['LMP_min']
        lmp_max = fila_limite['LMP_max']
        
        if variable not in datos.columns:
            continue
        
        # Filtrar datos del tipo de sistema correspondiente
        datos_filtrados = datos[datos['TipoSistema'] == tipo_sistema_limite]
        
        for _, fila_dato in datos_filtrados.iterrows():
            valor = fila_dato[variable]
            
            if pd.isna(valor):
                continue
            
            punto = fila_dato['Punto']
            campana = fila_dato['Campaña']
            tipo_sistema = fila_dato['TipoSistema']
            
            # Verificar incumplimiento
            incumple = False
            tipo_incumplimiento = ""
            
            if not pd.isna(lmp_min) and valor < lmp_min:
                incumple = True
                tipo_incumplimiento = f"Por debajo del minimo ({lmp_min})"
            elif not pd.isna(lmp_max) and valor > lmp_max:
                incumple = True
                tipo_incumplimiento = f"Por encima del maximo ({lmp_max})"
            
            if incumple:
                incumplimientos.append({
                    'Variable': variable,
                    'Punto': punto,
                    'Campaña': campana,
                    'TipoSistema': tipo_sistema,
                    'Valor': valor,
                    'LMP_Min': lmp_min,
                    'LMP_Max': lmp_max,
                    'Tipo_Incumplimiento': tipo_incumplimiento,
                    'Unidad': fila_limite['Unidad']
                })
    
    # Mostrar resumen
    if incumplimientos:
        print(f"Se encontraron {len(incumplimientos)} incumplimientos")
        
        # Agrupar por variable
        df_incumplimientos = pd.DataFrame(incumplimientos)
        print("\nIncumplimientos por variable:")
        for variable, group in df_incumplimientos.groupby('Variable'):
            print(f"  - {variable}: {len(group)} incumplimientos")
    else:
        print("No se encontraron incumplimientos")
    
    return incumplimientos

def calcular_porcentajes_incumplimiento(datos, limites):
    """
    Calcula porcentaje de no cumplimiento por punto y variable
    """
    print("Calculando porcentajes de incumplimiento...")
    
    porcentajes = []
    
    for _, fila_limite in limites.iterrows():
        variable = fila_limite['Variable']
        tipo_sistema_limite = fila_limite['TipoSistema']
        
        if variable not in datos.columns:
            continue
        
        # Filtrar datos del tipo de sistema correspondiente
        datos_filtrados = datos[datos['TipoSistema'] == tipo_sistema_limite]
        
        # Para cada punto en este tipo de sistema
        puntos = datos_filtrados['Punto'].unique()
        
        for punto in puntos:
            datos_punto = datos_filtrados[datos_filtrados['Punto'] == punto]
            datos_variable = datos_punto[variable].dropna()
            
            if len(datos_variable) == 0:
                continue
            
            lmp_min = fila_limite['LMP_min']
            lmp_max = fila_limite['LMP_max']
            
            # Contar incumplimientos
            count_incumplimientos = 0
            
            for valor in datos_variable:
                if not pd.isna(lmp_min) and valor < lmp_min:
                    count_incumplimientos += 1
                elif not pd.isna(lmp_max) and valor > lmp_max:
                    count_incumplimientos += 1
            
            porcentaje = (count_incumplimientos / len(datos_variable)) * 100
            
            porcentajes.append({
                'Variable': variable,
                'Punto': punto,
                'TipoSistema': tipo_sistema_limite,
                'Total_Mediciones': len(datos_variable),
                'Incumplimientos': count_incumplimientos,
                'Porcentaje_Incumplimiento': round(porcentaje, 2),
                'Unidad': fila_limite['Unidad']
            })
    
    # Mostrar resumen de porcentajes
    if porcentajes:
        df_porcentajes = pd.DataFrame(porcentajes)
        print("\nPorcentajes de incumplimiento mas altos:")
        df_top = df_porcentajes.nlargest(5, 'Porcentaje_Incumplimiento')
        for _, row in df_top.iterrows():
            print(f"  - {row['Variable']} en P{row['Punto']}: {row['Porcentaje_Incumplimiento']}%")
    
    return porcentajes

def identificar_puntos_criticos(incumplimientos):
    """
    Identifica las variables y puntos mas criticos por sistema
    """
    print("Identificando puntos mas criticos...")
    
    if not incumplimientos:
        print("  - No hay incumplimientos para analizar")
        return {}
    
    puntos_criticos = {
        'Potable': {},
        'Residual': {}, 
        'Rio': {}
    }
    
    # Agrupar incumplimientos manualmente
    for sistema in puntos_criticos.keys():
        # Filtrar incumplimientos para este sistema
        incumplimientos_sistema = [inc for inc in incumplimientos if inc['TipoSistema'] == sistema]
        
        if incumplimientos_sistema:
            # Contar por punto manualmente
            conteo_puntos = {}
            conteo_variables = {}
            
            for inc in incumplimientos_sistema:
                punto = inc['Punto']
                variable = inc['Variable']
                
                # Contar por punto
                conteo_puntos[punto] = conteo_puntos.get(punto, 0) + 1
                
                # Contar por variable
                conteo_variables[variable] = conteo_variables.get(variable, 0) + 1
            
            # Encontrar punto mas critico - forma segura
            punto_mas_critico = "N/A"
            count_punto = 0
            if conteo_puntos:
                # Encontrar el punto con mayor conteo manualmente
                for punto, count in conteo_puntos.items():
                    if count > count_punto:
                        count_punto = count
                        punto_mas_critico = punto
            
            # Encontrar variable mas critica - forma segura
            variable_mas_critica = "N/A"
            count_variable = 0
            if conteo_variables:
                # Encontrar la variable con mayor conteo manualmente
                for variable, count in conteo_variables.items():
                    if count > count_variable:
                        count_variable = count
                        variable_mas_critica = variable
            
            puntos_criticos[sistema] = {
                'punto_mas_critico': punto_mas_critico,
                'incumplimientos_punto': count_punto,
                'variable_mas_critica': variable_mas_critica,
                'incumplimientos_variable': count_variable,
                'total_incumplimientos': len(incumplimientos_sistema)
            }
            
            print(f"  - Sistema {sistema}:")
            print(f"    * Punto mas critico: P{punto_mas_critico} ({count_punto} incumplimientos)")
            print(f"    * Variable mas critica: {variable_mas_critica} ({count_variable} incumplimientos)")
            print(f"    * Total incumplimientos: {len(incumplimientos_sistema)}")
        else:
            print(f"  - Sistema {sistema}: No hay incumplimientos")
            puntos_criticos[sistema] = {}
    
    return puntos_criticos

def generar_graficas_incumplimientos(datos_organizados, limites, incumplimientos):
    """
    Genera graficas que destacan los valores que exceden limites
    """
    print("Generando graficas con incumplimientos destacados...")
    
    if not incumplimientos:
        print("  - No hay incumplimientos para graficar")
        return
    
    # Variables con incumplimientos
    variables_incumplimientos = list(set([inc['Variable'] for inc in incumplimientos]))
    
    for variable in variables_incumplimientos[:3]:  # Maximo 3 variables
        generar_grafica_incumplimientos_variable(datos_organizados['Todos'], variable, limites, incumplimientos)

def generar_grafica_incumplimientos_variable(datos, variable, limites, incumplimientos):
    """
    Genera grafica para una variable especifica destacando incumplimientos
    """
    plt.figure(figsize=(12, 6))
    
    # Filtrar incumplimientos para esta variable
    incumplimientos_var = [inc for inc in incumplimientos if inc['Variable'] == variable]
    
    # Colores por tipo de sistema
    colores = {'Rio': 'blue', 'Potable': 'green', 'Residual': 'red'}
    
    # Graficar todos los puntos
    for punto in datos['Punto'].unique():
        datos_punto = datos[datos['Punto'] == punto]
        tipo_sistema = datos_punto['TipoSistema'].iloc[0]
        color = colores.get(tipo_sistema, 'gray')
        
        # Separar puntos que cumplen vs no cumplen
        valores_cumplen = []
        valores_incumplen = []
        campanas_cumplen = []
        campanas_incumplen = []
        
        for _, fila in datos_punto.iterrows():
            campana = fila['Campaña']
            valor = fila[variable]
            
            if pd.isna(valor):
                continue
            
            # Verificar si este punto-campaña incumple
            incumple = any(inc['Punto'] == punto and inc['Campaña'] == campana and inc['Variable'] == variable 
                          for inc in incumplimientos_var)
            
            if incumple:
                valores_incumplen.append(valor)
                campanas_incumplen.append(campana)
            else:
                valores_cumplen.append(valor)
                campanas_cumplen.append(campana)
        
        # Graficar puntos que cumplen
        if valores_cumplen:
            x_pos = [list(datos['Punto'].unique()).index(punto)] * len(valores_cumplen)
            plt.scatter(x_pos, valores_cumplen, color=color, alpha=0.6, s=60, marker='o')
        
        # Graficar puntos que NO cumplen (mas grandes y con borde)
        if valores_incumplen:
            x_pos = [list(datos['Punto'].unique()).index(punto)] * len(valores_incumplen)
            plt.scatter(x_pos, valores_incumplen, color='red', alpha=0.8, s=100, marker='X', 
                       edgecolors='black', linewidth=2)
    
    # Agregar lineas de LMP
    lmp_info = obtener_lmp_variable(variable, limites)
    if lmp_info:
        lmp_valor = lmp_info['valor']
        if lmp_info['tipo'] == 'maximo':
            plt.axhline(y=lmp_valor, color='red', linestyle='--', linewidth=2,
                       label=f'LMP Max: {lmp_valor} {obtener_unidades(variable)}')
        elif lmp_info['tipo'] == 'minimo':
            plt.axhline(y=lmp_valor, color='blue', linestyle='--', linewidth=2,
                       label=f'LMP Min: {lmp_valor} {obtener_unidades(variable)}')
    
    plt.title(f'Incumplimientos de LMP - {variable}\n(X = Incumplimientos)')
    plt.xlabel('Puntos de Muestreo')
    plt.ylabel(f'{variable} ({obtener_unidades(variable)})')
    plt.xticks(range(len(datos['Punto'].unique())), sorted(datos['Punto'].unique()))
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Escala log para coliformes
    if 'Coli' in variable:
        plt.yscale('log')
        plt.ylabel(f'{variable} ({obtener_unidades(variable)}) - Escala Log')
    
    plt.tight_layout()
    plt.savefig(f'results/graficas/Incumplimientos_{variable}.png', dpi=300, bbox_inches='tight')
    plt.close()

def exportar_resultados_lmp(incumplimientos, porcentajes, puntos_criticos):
    """
    Exporta todos los resultados de evaluacion LMP a Excel
    """
    print("Exportando resultados LMP a Excel...")
    
    nombre_archivo = 'results/Resultados_LMP_VillaVerde.xlsx'
    
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        
        # Hoja 1: Incumplimientos detallados
        if incumplimientos:
            df_incumplimientos = pd.DataFrame(incumplimientos)
            df_incumplimientos.to_excel(writer, sheet_name='Incumplimientos_Detallados', index=False)
            print("  - Hoja creada: Incumplimientos_Detallados")
        
        # Hoja 2: Porcentajes de incumplimiento
        if porcentajes:
            df_porcentajes = pd.DataFrame(porcentajes)
            df_porcentajes.to_excel(writer, sheet_name='Porcentajes_Incumplimiento', index=False)
            print("  - Hoja creada: Porcentajes_Incumplimiento")
        
        # Hoja 3: Puntos criticos
        if puntos_criticos:
            datos_criticos = []
            for sistema, info in puntos_criticos.items():
                if info:
                    datos_criticos.append({
                        'Sistema': sistema,
                        'Punto_Mas_Critico': info.get('punto_mas_critico', 'N/A'),
                        'Incumplimientos_Punto': info.get('incumplimientos_punto', 0),
                        'Variable_Mas_Critica': info.get('variable_mas_critica', 'N/A'),
                        'Incumplimientos_Variable': info.get('incumplimientos_variable', 0),
                        'Total_Incumplimientos': info.get('total_incumplimientos', 0)
                    })
            
            if datos_criticos:
                df_criticos = pd.DataFrame(datos_criticos)
                df_criticos.to_excel(writer, sheet_name='Puntos_Criticos', index=False)
                print("  - Hoja creada: Puntos_Criticos")
    
    print(f"Archivo exportado: {nombre_archivo}")

# Funciones auxiliares (las mismas que en visualization.py)
def obtener_lmp_variable(variable, limites):
    """
    Obtiene informacion de LMP para una variable especifica
    """
    if limites is None or limites.empty:
        return None
    
    fila_limite = limites[limites['Variable'] == variable]
    
    if not fila_limite.empty:
        lmp_min = fila_limite['LMP_min'].iloc[0]
        lmp_max = fila_limite['LMP_max'].iloc[0]
        
        if pd.isnull(lmp_min) and not pd.isnull(lmp_max):
            return {'valor': lmp_max, 'tipo': 'maximo'}
        elif pd.isnull(lmp_max) and not pd.isnull(lmp_min):
            return {'valor': lmp_min, 'tipo': 'minimo'}
        elif not pd.isnull(lmp_min) and not pd.isnull(lmp_max):
            return {'valor': lmp_max, 'tipo': 'maximo'}
    
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
        'OD_mgL': 'mg/L'
    }
    return unidades.get(variable, '')
