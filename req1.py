"""
REQUERIMIENTO 1: LECTURA Y ORGANIZACION DE DATOS
Variables del grupo: Turbiedad, Color aparente, Coliformes totales, Coliformes fecales, Caudal, Precipitacion
"""

import pandas as pd

print("=== REQUERIMIENTO 1: LECTURA Y ORGANIZACION DE DATOS ===\n")

# 1. Cargar datos
print("1. Cargando datos desde Excel...")
datos = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Datos')
coordenadas = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Coordenadas')
limites = pd.read_excel('data/VillaVerde_WaterSystemData.xlsx', sheet_name='Limites')

print("Datos cargados exitosamente")
print(f"  - Datos principales: {datos.shape[0]} filas, {datos.shape[1]} columnas")
print(f"  - Coordenadas: {coordenadas.shape[0]} puntos")
print(f"  - Limites: {limites.shape[0]} regulaciones")

# 2. Filtrar solo las variables de nuestro grupo
variables_grupo = ['Turb_NTU', 'Color_PtCo', 'Coli_tot_NMP100mL', 'Coli_fec_NMP100mL', 'Caudal_Ls', 'Precip_mm_d']
columnas_mantener = ['Punto', 'TipoSistema', 'Campaña'] + variables_grupo

datos_filtrados = datos[columnas_mantener].copy()

# 3. Unir con coordenadas (usar la columna correcta)
datos_completos = datos_filtrados.merge(coordenadas[['Punto', 'Descripcion']], 
                                       on='Punto', how='left')

print("\nColumnas disponibles después del merge:")
print(datos_completos.columns.tolist())

# 4. Organizar por tipo de sistema (usar la columna correcta)
potable = datos_completos[datos_completos['TipoSistema'] == 'Potable']
residual = datos_completos[datos_completos['TipoSistema'] == 'Residual']
rio = datos_completos[datos_completos['TipoSistema'] == 'Rio']

print("\n2. Datos organizados por tipo de sistema:")
print(f"  - Potable: {len(potable)} registros")
print(f"  - Residual: {len(residual)} registros") 
print(f"  - Rio: {len(rio)} registros")

# 5. Mostrar informacion basica
print("\n3. Informacion de datos:")
print(f"Puntos de monitoreo: {list(datos_completos['Punto'].unique())}")
print(f"Campañas: {list(datos_completos['Campaña'].unique())}")
print(f"Variables de nuestro grupo: {variables_grupo}")

# 6. Mostrar limites cargados
print("\n4. Limites permisibles cargados:")
limites_grupo = limites[limites['Variable'].isin(variables_grupo)]
for index, fila in limites_grupo.iterrows():
    lmp_min = fila['LMP_min']
    lmp_max = fila['LMP_max']
    
    # Verificar de forma simple
    if lmp_min != lmp_min:  # Esto detecta NaN
        print(f"  - {fila['Variable']}: max {lmp_max} {fila['Unidad']}")
    elif lmp_max != lmp_max:  # Esto detecta NaN
        print(f"  - {fila['Variable']}: min {lmp_min} {fila['Unidad']}")
    else:
        print(f"  - {fila['Variable']}: {lmp_min}-{lmp_max} {fila['Unidad']}")

# 7. Vista previa
print("\n5. Vista previa de datos (primeras 2 filas por sistema):")
print("\nPotable:")
print(potable.head(2))
print("\nResidual:")
print(residual.head(2)) 
print("\nRio:")
print(rio.head(2))

print("\nREQUERIMIENTO 1 COMPLETADO")
