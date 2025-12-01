"""""
TRABAJO FINAL - ANALISIS CALIDAD DEL AGUA VILLA VERDE
Grupo: Los mas gays
Integrantes: Gay1, gay2 y gay2
Fecha: Diciembre 2025

Requerimiento i: Lectura y organizacion de datos
Requerimiento ii: Estadistica descriptiva
"""

from modules.data_loader import cargar_datos, organizar_datos, explorar_datos, validar_estructura_datos
from modules.descriptive_stats import calcular_estadisticas, mostrar_resumen_estadisticas
from modules.lmp_analysis import evaluar_limites_permitidos
from modules.visualization import generar_graficas_patrones

def main():
    """
    Funcion principal que ejecuta todo el analisis de calidad del agua
    """
    print("=== INICIANDO ANALISIS DE CALIDAD DEL AGUA - VILLA VERDE ===\n")
    
    # i. LECTURA Y ORGANIZACION DE DATOS
    print("=" * 60)
    print("REQUERIMIENTO i: LECTURA Y ORGANIZACION DE DATOS")
    print("=" * 60)
    
    # 1. Cargar datos desde archivos Excel
    print("\n1. Cargando datos desde archivos Excel...")
    datos, coordenadas, limites = cargar_datos()
    
    if datos is None:
        print("No se pudieron cargar los datos. Verifica los archivos.")
        return
    
    # 2. Organizar datos por punto, variable, campaña y tipo de sistema
    print("\n2. Organizando datos por tipo de sistema...")
    datos_organizados = organizar_datos(datos, coordenadas)
    
    if not datos_organizados:
        print("No se pudieron organizar los datos.")
        return
    
    # 3. Explorar estructura de datos
    explorar_datos(datos_organizados)
    
    # 4. Validar estructura de datos
    estructura_valida = validar_estructura_datos(datos_organizados)
    
    if not estructura_valida:
        print("La estructura de datos no es valida para el analisis.")
        return
    
    print("\n" + "=" * 60)
    print("REQUERIMIENTO i COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    
    # Mostrar preview de datos organizados
    print("\n--- VISTA PREVIA DE DATOS ORGANIZADOS ---")
    for tipo_sistema, df in datos_organizados.items():
        if not df.empty:
            print(f"\n{tipo_sistema} (primeras 3 filas):")
            print(df[['Punto', 'TipoSistema', 'Campaña', 'Turb_NTU', 'DBO5_mgL', 'Coli_fec_NMP100mL']].head(3))
    
    # Mostrar informacion de limites cargados
    if limites is not None and not limites.empty:
        print(f"\n--- INFORMACION DE LIMITES CARGADOS ---")
        print(f"Limites cargados: {len(limites)} regulaciones")
        print("Variables con limites definidos:")
        for _index, row in limites.iterrows():
            lmp_min = row['LMP_min']
            lmp_max = row['LMP_max']
        
            # Verificar usando comparación directa con None y NaN
            if lmp_min is None or lmp_min != lmp_min:  # lmp_min != lmp_min detecta NaN
                print(f"  - {row['Variable']}: max {lmp_max} {row['Unidad']} ({row['Uso']})")
            elif lmp_max is None or lmp_max != lmp_max:  # lmp_max != lmp_max detecta NaN
                print(f"  - {row['Variable']}: min {lmp_min} {row['Unidad']} ({row['Uso']})")
            else:
                print(f"  - {row['Variable']}: {lmp_min}-{lmp_max} {row['Unidad']} ({row['Uso']})")
    else:
        print("\n--- INFORMACION DE LIMITES CARGADOS ---")
        print("No se pudieron cargar los limites permisibles")    

    # ii. ESTADISTICA DESCRIPTIVA
    print("\n" + "=" * 60)
    print("REQUERIMIENTO ii: ESTADISTICA DESCRIPTIVA")
    print("=" * 60)
    
    # 5. Calcular estadisticas descriptivas
    print("\n5. Calculando estadisticas descriptivas...")
    resultados_estadisticas = calcular_estadisticas(datos_organizados)
    
    # 6. Mostrar resumen de estadisticas
    mostrar_resumen_estadisticas(resultados_estadisticas)
    
    print("\n" + "=" * 60)
    print("REQUERIMIENTO ii COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    
    # iii. ANALISIS GRAFICO
    print("\n" + "=" * 60)
    print("REQUERIMIENTO iii: ANALISIS GRAFICO")
    print("=" * 60)
    
    # 7. Generar graficas de patrones espaciales y temporales
    print("\n7. Generando graficas de analisis...")
    generar_graficas_patrones(datos_organizados, limites)
    
    print("\n" + "=" * 60)
    print("REQUERIMIENTO iii COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("REQUERIMIENTO iv: EVALUACION LIMITES MAXIMOS PERMISIBLES")
    print("=" * 60)
    
    # 8. Evaluar cumplimiento de limites
    print("\n8. Evaluando cumplimiento de limites...")
    evaluar_limites_permitidos(datos_organizados, limites)
    
    print("\n" + "=" * 60)
    print("REQUERIMIENTO iv COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    
    print("Resultados guardados en la carpeta 'results/'")

if __name__ == "__main__":
    main()
