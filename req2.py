"""
REQUERIMIENTO 2: ESTADISTICA DESCRIPTIVA
"""

import pandas as pd

print("=== REQUERIMIENTO 2: ESTADISTICA DESCRIPTIVA ===\n")

print("Cargando y organizando datos...")

# Cargar datos directamente (sin importar req1)
datos = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Datos')
coordenadas = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Coordenadas')

# Variables de nuestro grupo
variables_grupo = ['Turb_NTU', 'Color_PtCo', 'Coli_tot_NMP100mL', 'Coli_fec_NMP100mL', 'Caudal_Ls', 'Precip_mm_d']
columnas_mantener = ['Punto', 'TipoSistema', 'Campaña'] + variables_grupo

datos_filtrados = datos[columnas_mantener].copy()
datos_completos = datos_filtrados.merge(coordenadas[['Punto', 'Descripcion']], on='Punto', how='left')

# Organizar por tipo de sistema
potable = datos_completos[datos_completos['TipoSistema'] == 'Potable']
residual = datos_completos[datos_completos['TipoSistema'] == 'Residual']
rio = datos_completos[datos_completos['TipoSistema'] == 'Rio']

print("Calculando estadisticas descriptivas...")

# Lista para guardar todos los resultados
resultados = []

# a. Estadisticas por puntos de muestreo - MANUAL
print("\n1. Estadisticas por punto de muestreo:")

for sistema, datos_sistema in [('Potable', potable), ('Residual', residual), ('Rio', rio)]:
    if len(datos_sistema) > 0:
        print(f"  - Calculando {sistema}...")
        
        # Obtener puntos manualmente
        puntos = []
        for i in range(len(datos_sistema)):
            punto = datos_sistema.iloc[i]['Punto']
            if punto not in puntos:
                puntos.append(punto)
        
        # Calcular estadisticas para cada punto
        stats_por_punto = []
        
        for punto in puntos:
            # Recolectar valores para cada variable manualmente
            stats_fila = {'Punto': punto}
            
            for variable in variables_grupo:
                if variable in datos_sistema.columns:
                    # Recolectar todos los valores de esta variable para este punto
                    valores = []
                    for i in range(len(datos_sistema)):
                        if datos_sistema.iloc[i]['Punto'] == punto:
                            valor = datos_sistema.iloc[i][variable]
                            if valor == valor and valor is not None:  # Filtrar NaN
                                valores.append(valor)
                    
                    if valores:
                        # Calcular manualmente
                        min_val = min(valores)
                        max_val = max(valores)
                        mean_val = sum(valores) / len(valores)
                        
                        # Desviación estándar manual
                        suma_cuadrados = 0
                        for v in valores:
                            suma_cuadrados += (v - mean_val) ** 2
                        std_val = (suma_cuadrados / len(valores)) ** 0.5
                        
                        stats_fila[f'{variable}_min'] = round(min_val, 3)
                        stats_fila[f'{variable}_max'] = round(max_val, 3)
                        stats_fila[f'{variable}_mean'] = round(mean_val, 3)
                        stats_fila[f'{variable}_std'] = round(std_val, 3)
            
            stats_por_punto.append(stats_fila)
        
        if stats_por_punto:
            df_stats = pd.DataFrame(stats_por_punto)
            resultados.append((f'{sistema}_Puntos', df_stats))

# b. Estadisticas por campañas para cada punto - MANUAL
print("\n2. Estadisticas por campaña para cada punto:")

for sistema, datos_sistema in [('Potable', potable), ('Residual', residual), ('Rio', rio)]:
    if len(datos_sistema) > 0:
        print(f"  - Calculando {sistema}...")
        
        # Obtener puntos manualmente
        puntos = []
        for i in range(len(datos_sistema)):
            punto = datos_sistema.iloc[i]['Punto']
            if punto not in puntos:
                puntos.append(punto)
        
        for punto in puntos:
            # Recolectar datos por campaña manualmente
            datos_por_campana = {}
            
            for i in range(len(datos_sistema)):
                if datos_sistema.iloc[i]['Punto'] == punto:
                    campana = datos_sistema.iloc[i]['Campaña']
                    if campana not in datos_por_campana:
                        datos_por_campana[campana] = {}
                    
                    for variable in variables_grupo:
                        if variable in datos_sistema.columns:
                            valor = datos_sistema.iloc[i][variable]
                            if valor == valor and valor is not None:  # Filtrar NaN
                                datos_por_campana[campana][variable] = valor
            
            # Convertir a formato para Excel
            stats_por_campana = []
            for campana, valores in datos_por_campana.items():
                fila = {'Campaña': campana}
                fila.update(valores)
                stats_por_campana.append(fila)
            
            if stats_por_campana:
                df_stats = pd.DataFrame(stats_por_campana)
                nombre_hoja = f'{sistema}_P{punto}'[:31]
                resultados.append((nombre_hoja, df_stats))

# Guardar todo en Excel
if resultados:
    with pd.ExcelWriter('results/estadisticas.xlsx') as writer:
        for nombre_hoja, datos in resultados:
            datos.to_excel(writer, sheet_name=nombre_hoja, index=False)
    print(f"\nArchivo guardado: results/estadisticas.xlsx")
else:
    print("\nNo se pudieron calcular estadisticas")

# 3. Mostrar resumen simple
print("\n3. Resumen de promedios:")
for sistema, datos_sistema in [('Potable', potable), ('Residual', residual), ('Rio', rio)]:
    if len(datos_sistema) > 0:
        print(f"\n{sistema}:")
        for variable in variables_grupo[:2]:  # Solo 2 variables
            if variable in datos_sistema.columns:
                # Calcular promedio manualmente
                valores = []
                for i in range(len(datos_sistema)):
                    valor = datos_sistema.iloc[i][variable]
                    if valor == valor and valor is not None:
                        valores.append(valor)
                
                if valores:
                    promedio = sum(valores) / len(valores)
                    print(f"  - {variable}: {promedio:.2f}")

print("\nREQUERIMIENTO 2 COMPLETADO")
