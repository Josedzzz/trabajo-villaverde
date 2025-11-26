"""
Módulo para carga y organización de datos - Villa Verde
Requerimiento i: Lectura y organización de datos
"""

import pandas as pd
import os

def cargar_datos():
    """
    Carga todos los archivos de datos necesarios desde el Excel
    
    Returns:
        tuple: (datos_principales, coordenadas, limites_permitidos)
    """
    try:
        if not os.path.exists('data/VillaVerde_WaterSystemData.xlsx'):
            print("Error: El archivo de datos no existe en la carpeta 'data/'")
            return None, None, None
        
        datos = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Datos')
        coordenadas = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Coordenadas')
        limites = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Limites')
        
        print("Datos cargados exitosamente")
        print(f"  - Datos principales: {datos.shape[0]} filas, {datos.shape[1]} columnas")
        print(f"  - Coordenadas: {coordenadas.shape[0]} puntos")
        print(f"  - Límites: {limites.shape[0]} regulaciones")
        
        return datos, coordenadas, limites
        
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return None, None, None

def organizar_datos(datos, coordenadas):
    """
    Organiza los datos por punto, variable, campaña y tipo de sistema
    
    Args:
        datos: DataFrame con datos principales
        coordenadas: DataFrame con información de puntos
    
    Returns:
        dict: Diccionario con datos organizados para análisis
    """
    if datos is None or datos.empty:
        print("No hay datos para organizar")
        return {}
    
    # 1. Unir datos con información de coordenadas y tipo de sistema
    print("\nOrganizando datos...")
    
    # Verificar que las columnas necesarias existen
    columnas_requeridas = ['Punto', 'TipoSistema', 'Campaña']
    for col in columnas_requeridas:
        if col not in datos.columns:
            print(f"Columna requerida '{col}' no encontrada en los datos")
            return {}
    
    # Unir con coordenadas para tener información completa de cada punto
    datos_completos = datos.merge(coordenadas[['Punto', 'TipoSistema', 'Descripcion']], 
                                 on='Punto', how='left', suffixes=('', '_coord'))
    
    # 2. Organizar por tipo de sistema (como requiere el PDF)
    datos_organizados = {
        'Potable': datos_completos[datos_completos['TipoSistema'] == 'Potable'].copy(),
        'Residual': datos_completos[datos_completos['TipoSistema'] == 'Residual'].copy(),
        'Rio': datos_completos[datos_completos['TipoSistema'] == 'Rio'].copy(),
        'Todos': datos_completos.copy()
    }
    
    # 3. Mostrar resumen de la organización
    print("Datos organizados por tipo de sistema:")
    for tipo, df in datos_organizados.items():
        if not df.empty:
            puntos_unicos = df['Punto'].unique()
            campanas_unicas = df['Campaña'].unique()
            print(f"  - {tipo}: {len(df)} registros, Puntos: {list(puntos_unicos)}, Campañas: {list(campanas_unicas)}")
    
    return datos_organizados

def explorar_datos(datos_organizados):
    """
    Función exploratoria para entender la estructura de los datos
    """
    if not datos_organizados:
        return
    
    print("\n--- EXPLORACIÓN DE DATOS ---")
    datos_todos = datos_organizados['Todos']
    
    # Información general
    print(f"Total de registros: {len(datos_todos)}")
    print(f"Total de variables: {len(datos_todos.columns)}")
    print(f"Período de campañas: {sorted(datos_todos['Campaña'].unique())}")
    
    # Puntos de monitoreo
    puntos = datos_todos['Punto'].unique()
    print(f"Puntos de monitoreo: {list(puntos)}")
    
    # Variables disponibles (excluyendo columnas de identificación)
    columnas_id = ['Punto', 'TipoSistema', 'Campaña', 'Descripcion']
    variables = [col for col in datos_todos.columns if col not in columnas_id]
    print(f"Variables de calidad: {variables}")
    
    # Datos faltantes por variable
    print("\nDatos faltantes por variable:")
    for variable in variables:
        faltantes = datos_todos[variable].isna().sum()
        total = len(datos_todos)
        if faltantes > 0:
            print(f"  - {variable}: {faltantes}/{total} ({faltantes/total*100:.1f}%)")

def validar_estructura_datos(datos_organizados):
    """
    Valida que los datos tengan la estructura esperada para el análisis
    """
    print("\n--- VALIDACIÓN DE ESTRUCTURA ---")
    
    if not datos_organizados:
        print("No hay datos organizados para validar")
        return False
    
    datos_todos = datos_organizados['Todos']
    
    # Verificar que tenemos todos los puntos P1-P8
    puntos_esperados = [f'P{i}' for i in range(1, 9)]
    puntos_encontrados = datos_todos['Punto'].unique()
    
    puntos_faltantes = set(puntos_esperados) - set(puntos_encontrados)
    if puntos_faltantes:
        print(f"Puntos faltantes: {puntos_faltantes}")
        return False
    else:
        print("Todos los puntos P1-P8 presentes")
    
    # Verificar que tenemos las 4 campañas
    campanas_esperadas = ['C1', 'C2', 'C3', 'C4']
    campanas_encontradas = datos_todos['Campaña'].unique()
    
    campanas_faltantes = set(campanas_esperadas) - set(campanas_encontradas)
    if campanas_faltantes:
        print(f"Campañas faltantes: {campanas_faltantes}")
        return False
    else:
        print("Todas las campañas C1-C4 presentes")
    
    # Verificar que tenemos datos para cada tipo de sistema
    for tipo in ['Potable', 'Residual', 'Rio']:
        if datos_organizados[tipo].empty:
            print(f"No hay datos para el sistema: {tipo}")
            return False
        else:
            print(f"Datos presentes para sistema: {tipo}")
    
    print("Estructura de datos validada correctamente")
    return True
