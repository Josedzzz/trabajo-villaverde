"""
Modulo para estadistica descriptiva - Villa Verde
Requerimiento ii: Estadistica descriptiva
"""

import pandas as pd
import os

def calcular_estadisticas(datos_organizados):
    """
    Calcula estadisticas descriptivas para cada variable segun requerimientos:
    a. Por puntos de muestreo, diferenciando tipo de sistema
    b. Por campañas para cada punto
    
    Args:
        datos_organizados: Diccionario con datos organizados por tipo de sistema
    
    Returns:
        dict: Diccionario con todos los resultados estadisticos
    """
    if not datos_organizados:
        print("No hay datos organizados para calcular estadisticas")
        return {}
    
    # Obtener lista de variables SOLO NUMERICAS
    datos_todos = datos_organizados['Todos']
    columnas_no_numericas = ['Punto', 'TipoSistema', 'Campaña', 'Descripcion', 'X_UTM', 'Y_UTM', 'TipoSistema_coord']
    
    # Filtrar solo columnas numéricas
    variables_numericas = []
    for col in datos_todos.columns:
        if col not in columnas_no_numericas:
            # Verificar si la columna es numérica
            if pd.api.types.is_numeric_dtype(datos_todos[col]):
                variables_numericas.append(col)
    
    print(f"Variables numericas a analizar: {variables_numericas}")
    
    # Crear directorio de resultados si no existe
    os.makedirs('results', exist_ok=True)
    
    # Calcular estadisticas para cada tipo de sistema
    resultados = {}
    
    for tipo_sistema, datos in datos_organizados.items():
        if datos.empty:
            continue
            
        print(f"\n--- Calculando estadisticas para: {tipo_sistema} ---")
        
        # a. Estadisticas por puntos de muestreo
        stats_por_punto = calcular_stats_por_punto(datos, variables_numericas, tipo_sistema)
        
        # b. Estadisticas por campañas para cada punto
        stats_por_campana_punto = calcular_stats_por_campana_punto(datos, variables_numericas, tipo_sistema)
        
        resultados[tipo_sistema] = {
            'por_puntos': stats_por_punto,
            'por_campana_punto': stats_por_campana_punto
        }
    
    # Exportar todos los resultados a Excel
    exportar_resultados_excel(resultados)
    
    print("\nEstadisticas descriptivas calculadas exitosamente")
    return resultados

def calcular_stats_por_punto(datos, variables, tipo_sistema):
    """
    Calcula estadisticas para cada variable entre puntos de muestreo
    
    Args:
        datos: DataFrame con datos del tipo de sistema
        variables: Lista de variables numericas
        tipo_sistema: Tipo de sistema (Potable, Residual, Rio)
    
    Returns:
        DataFrame: Estadisticas por punto
    """
    print(f"  - Calculando estadisticas por punto para {tipo_sistema}...")
    
    # Filtrar solo las filas que tienen datos numericos
    datos_filtrados = datos[['Punto'] + variables].copy()
    
    # Agrupar por punto y calcular estadisticas para cada variable
    stats_punto = datos_filtrados.groupby('Punto')[variables].agg([
        'count', 'min', 'max', 'mean', 'std'
    ]).round(3)
    
    # Renombrar columnas para mejor legibilidad
    stats_punto.columns = ['_'.join(col).strip() for col in stats_punto.columns.values]
    
    return stats_punto

def calcular_stats_por_campana_punto(datos, variables, tipo_sistema):
    """
    Calcula estadisticas para cada variable entre campañas para cada punto
    
    Args:
        datos: DataFrame con datos del tipo de sistema
        variables: Lista de variables numericas
        tipo_sistema: Tipo de sistema (Potable, Residual, Rio)
    
    Returns:
        dict: Diccionario con DataFrames por punto
    """
    print(f"  - Calculando estadisticas por campaña/punto para {tipo_sistema}...")
    
    stats_por_punto = {}
    
    # Para cada punto en este tipo de sistema, calcular stats por campaña
    puntos = datos['Punto'].unique()
    
    for punto in puntos:
        datos_punto = datos[datos['Punto'] == punto]
        
        # Filtrar solo columnas numericas
        datos_punto_filtrados = datos_punto[['Campaña'] + variables].copy()
        
        # Agrupar por campaña y calcular estadisticas
        stats_campana = datos_punto_filtrados.groupby('Campaña')[variables].agg([
            'min', 'max', 'mean', 'std'
        ]).round(3)
        
        # Renombrar columnas
        stats_campana.columns = ['_'.join(col).strip() for col in stats_campana.columns.values]
        
        stats_por_punto[punto] = stats_campana
    
    return stats_por_punto

def exportar_resultados_excel(resultados):
    """
    Exporta todos los resultados estadisticos a un archivo Excel
    
    Args:
        resultados: Diccionario con todos los resultados estadisticos
    """
    print("\n--- Exportando resultados a Excel ---")
    
    nombre_archivo = 'results/Resultados_VillaVerde_Estadisticas.xlsx'
    
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        
        # Para cada tipo de sistema, crear hojas en el Excel
        for tipo_sistema, stats in resultados.items():
            if not stats['por_puntos'].empty:
                # Hoja: Estadisticas por punto
                nombre_hoja = f'{tipo_sistema}_PorPunto'
                stats['por_puntos'].to_excel(writer, sheet_name=nombre_hoja)
                print(f"  - Hoja creada: {nombre_hoja}")
            
            # Hojas: Estadisticas por campaña para cada punto
            for punto, df_campana in stats['por_campana_punto'].items():
                if not df_campana.empty:
                    nombre_hoja = f'{tipo_sistema}_P{punto}_PorCampana'
                    # Limitar nombre de hoja a 31 caracteres (limite de Excel)
                    nombre_hoja = nombre_hoja[:31]
                    df_campana.to_excel(writer, sheet_name=nombre_hoja)
                    print(f"  - Hoja creada: {nombre_hoja}")
        
        # Hoja resumen con estadisticas generales
        crear_hoja_resumen(writer, resultados)
    
    print(f"Archivo exportado: {nombre_archivo}")

def crear_hoja_resumen(writer, resultados):
    """
    Crea una hoja de resumen con las estadisticas mas importantes
    """
    print("  - Creando hoja de resumen...")
    
    resumen_data = []
    
    for tipo_sistema, stats in resultados.items():
        if stats['por_puntos'].empty:
            continue
            
        # Obtener las variables disponibles
        variables = [col.split('_')[0] for col in stats['por_puntos'].columns if '_count' in col]
        
        for variable in variables:
            # Buscar el punto con el valor maximo y minimo para esta variable
            col_mean = f'{variable}_mean'
            col_std = f'{variable}_std'
            
            if col_mean in stats['por_puntos'].columns:
                mean_values = stats['por_puntos'][col_mean]
                std_values = stats['por_puntos'][col_std]
                
                if not mean_values.empty:
                    punto_max = mean_values.idxmax()
                    valor_max = mean_values.max()
                    punto_min = mean_values.idxmin()
                    valor_min = mean_values.min()
                    avg_std = std_values.mean()
                    
                    resumen_data.append({
                        'Tipo_Sistema': tipo_sistema,
                        'Variable': variable,
                        'Punto_Mayor_Media': punto_max,
                        'Media_Maxima': valor_max,
                        'Punto_Menor_Media': punto_min,
                        'Media_Minima': valor_min,
                        'Desviacion_Promedio': avg_std
                    })
    
    if resumen_data:
        df_resumen = pd.DataFrame(resumen_data)
        df_resumen.to_excel(writer, sheet_name='Resumen_General', index=False)

def mostrar_resumen_estadisticas(resultados):
    """
    Muestra un resumen por consola de las estadisticas calculadas
    """
    print("\n" + "="*60)
    print("RESUMEN ESTADISTICAS DESCRIPTIVAS")
    print("="*60)
    
    for tipo_sistema, stats in resultados.items():
        print(f"\n--- {tipo_sistema.upper()} ---")
        
        if not stats['por_puntos'].empty:
            print("Estadisticas por punto:")
            # Mostrar solo algunas variables clave para no saturar
            variables_clave = ['Turb_NTU', 'DBO5_mgL', 'Coli_fec_NMP100mL', 'pH', 'OD_mgL']
            
            for variable in variables_clave:
                col_mean = f'{variable}_mean'
                if col_mean in stats['por_puntos'].columns:
                    print(f"  {variable}:")
                    for punto, row in stats['por_puntos'].iterrows():
                        mean_val = row[col_mean]
                        std_val = row[f'{variable}_std']
                        print(f"    P{punto}: {mean_val:.3f} ± {std_val:.3f}")
