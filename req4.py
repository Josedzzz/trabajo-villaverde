"""
REQUERIMIENTO 4: EVALUACION DE LIMITES MAXIMOS PERMISIBLES
Variables del grupo: Turbiedad, Color aparente, Coliformes totales, Coliformes fecales, Caudal, Precipitacion
"""

import pandas as pd
import matplotlib.pyplot as plt

print("=== REQUERIMIENTO 4: EVALUACION LMP ===\n")

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

print("Evaluando cumplimiento de limites...")

# 1. Identificar incumplimientos
incumplimientos = []

# Recorrer limites manualmente
for i_limite in range(len(limites)):
    fila_limite = limites.iloc[i_limite]
    variable = fila_limite['Variable']
    
    if variable not in variables_grupo:
        continue
        
    lmp_min = fila_limite['LMP_min']
    lmp_max = fila_limite['LMP_max']
    tipo_sistema_limite = fila_limite['TipoSistema']
    unidad = fila_limite['Unidad']
    
    # Filtrar datos del tipo de sistema correspondiente manualmente
    for i_dato in range(len(datos_completos)):
        tipo_sistema_dato = datos_completos.iloc[i_dato]['TipoSistema']
        
        if tipo_sistema_dato == tipo_sistema_limite:
            valor = datos_completos.iloc[i_dato][variable]
            if valor != valor:  # Saltar NaN
                continue
                
            punto = datos_completos.iloc[i_dato]['Punto']
            campana = datos_completos.iloc[i_dato]['Campaña']
            
            # Verificar incumplimiento
            if lmp_min == lmp_min and valor < lmp_min:  # lmp_min no es NaN
                incumplimientos.append({
                    'Variable': variable,
                    'Punto': punto,
                    'Campaña': campana,
                    'Valor': valor,
                    'LMP': lmp_min,
                    'Tipo': 'Por debajo del minimo',
                    'Unidad': unidad
                })
            elif lmp_max == lmp_max and valor > lmp_max:  # lmp_max no es NaN
                incumplimientos.append({
                    'Variable': variable,
                    'Punto': punto,
                    'Campaña': campana,
                    'Valor': valor,
                    'LMP': lmp_max,
                    'Tipo': 'Por encima del maximo',
                    'Unidad': unidad
                })

# 2. Mostrar resultados
print("\n1. Incumplimientos encontrados:")
if incumplimientos:
    print(f"Total de incumplimientos: {len(incumplimientos)}")
    
    # Agrupar por variable manualmente
    conteo_variables = {}
    for inc in incumplimientos:
        variable = inc['Variable']
        conteo_variables[variable] = conteo_variables.get(variable, 0) + 1
    
    print("\nPor variable:")
    for variable, count in conteo_variables.items():
        print(f"  - {variable}: {count} incumplimientos")
    
    # Agrupar por punto manualmente
    conteo_puntos = {}
    for inc in incumplimientos:
        punto = inc['Punto']
        conteo_puntos[punto] = conteo_puntos.get(punto, 0) + 1
    
    print("\nPor punto:")
    for punto, count in conteo_puntos.items():
        print(f"  - P{punto}: {count} incumplimientos")
else:
    print("No se encontraron incumplimientos")

# 3. Calcular porcentajes de no cumplimiento
print("\n2. Porcentajes de no cumplimiento:")

porcentajes = []

for variable in variables_grupo:
    # Buscar limite para esta variable manualmente
    lmp_max_encontrado = None
    for i_limite in range(len(limites)):
        fila_limite = limites.iloc[i_limite]
        if fila_limite['Variable'] == variable:
            lmp_max_encontrado = fila_limite['LMP_max']
            break
    
    if lmp_max_encontrado is not None and lmp_max_encontrado == lmp_max_encontrado:  # No es NaN
        # Contar mediciones totales e incumplimientos
        total_mediciones = 0
        incumplimientos_count = 0
        
        for i in range(len(datos_completos)):
            valor = datos_completos.iloc[i][variable]
            if valor == valor:  # No es NaN
                total_mediciones += 1
                if valor > lmp_max_encontrado:
                    incumplimientos_count += 1
        
        if total_mediciones > 0:
            porcentaje = (incumplimientos_count / total_mediciones) * 100
            porcentajes.append({
                'Variable': variable,
                'Porcentaje_Incumplimiento': round(porcentaje, 2),
                'Total_Mediciones': total_mediciones,
                'Incumplimientos': incumplimientos_count
            })

# Mostrar porcentajes
for p in porcentajes:
    print(f"  - {p['Variable']}: {p['Porcentaje_Incumplimiento']}% ({p['Incumplimientos']}/{p['Total_Mediciones']})")

# 4. Identificar puntos mas criticos
print("\n3. Puntos mas criticos por sistema:")

sistemas = ['Potable', 'Residual', 'Rio']
for sistema in sistemas:
    # Filtrar incumplimientos del sistema manualmente
    incumplimientos_sistema = []
    for inc in incumplimientos:
        # Verificar si el punto pertenece al sistema
        punto_pertenece = False
        for i in range(len(datos_completos)):
            if datos_completos.iloc[i]['Punto'] == inc['Punto'] and datos_completos.iloc[i]['TipoSistema'] == sistema:
                punto_pertenece = True
                break
        
        if punto_pertenece:
            incumplimientos_sistema.append(inc)
    
    if incumplimientos_sistema:
        # Contar por punto manualmente
        conteo_puntos = {}
        for inc in incumplimientos_sistema:
            punto = inc['Punto']
            conteo_puntos[punto] = conteo_puntos.get(punto, 0) + 1
        
        # Encontrar punto mas critico
        punto_mas_critico = None
        max_incumplimientos = 0
        for punto, count in conteo_puntos.items():
            if count > max_incumplimientos:
                max_incumplimientos = count
                punto_mas_critico = punto
        
        print(f"  - {sistema}: P{punto_mas_critico} ({max_incumplimientos} incumplimientos)")
    else:
        print(f"  - {sistema}: Sin incumplimientos")

# 5. GENERAR GRAFICAS CON LMP
print("\n4. Generando graficas con limites maximos permisibles...")

variables_con_limites = ['Turb_NTU', 'Coli_fec_NMP100mL']  # Variables que tienen LMP

for variable in variables_con_limites:
    plt.figure(figsize=(12, 6))
    
    # Buscar LMP para esta variable
    lmp_max = None
    for i_limite in range(len(limites)):
        fila_limite = limites.iloc[i_limite]
        if fila_limite['Variable'] == variable:
            lmp_max = fila_limite['LMP_max']
            break
    
    # Graficar todos los puntos
    puntos = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']
    colores = {'Rio': 'blue', 'Potable': 'green', 'Residual': 'red'}
    
    for punto in puntos:
        datos_punto = datos_completos[datos_completos['Punto'] == punto]
        if len(datos_punto) > 0:
            # Calcular promedio manual
            valores = []
            for i in range(len(datos_punto)):
                valor = datos_punto.iloc[i][variable]
                if valor == valor:
                    valores.append(valor)
            
            if valores:
                promedio = sum(valores) / len(valores)
                color = colores.get(datos_punto.iloc[0]['TipoSistema'], 'gray')
                plt.bar(punto, promedio, color=color, alpha=0.7)
    
    # Agregar linea de LMP
    if lmp_max is not None and lmp_max == lmp_max:
        plt.axhline(y=lmp_max, color='red', linestyle='--', linewidth=2, 
                   label=f'LMP Max: {lmp_max}')
    
    plt.title(f'Evaluacion LMP - {variable}\nLinea roja = Limite Maximo Permisible')
    plt.xlabel('Puntos de Muestreo')
    unidades = {'Turb_NTU': 'NTU', 'Coli_fec_NMP100mL': 'NMP/100mL'}
    plt.ylabel(f'{variable} ({unidades.get(variable, "")})')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f'results/graficas/lmp_{variable}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Grafica guardada: lmp_{variable}.png")

# 6. Exportar resultados
print("\n5. Exportando resultados...")

with pd.ExcelWriter('results/resultados_lmp.xlsx') as writer:
    if incumplimientos:
        df_incumplimientos = pd.DataFrame(incumplimientos)
        df_incumplimientos.to_excel(writer, sheet_name='Incumplimientos', index=False)
        print("  - Hoja creada: Incumplimientos")
    
    if porcentajes:
        df_porcentajes = pd.DataFrame(porcentajes)
        df_porcentajes.to_excel(writer, sheet_name='Porcentajes', index=False)
        print("  - Hoja creada: Porcentajes")

print("\nREQUERIMIENTO 4 COMPLETADO")
print("Resultados guardados en 'results/resultados_lmp.xlsx'")
print("Graficas con LMP guardadas en 'results/graficas/'")
