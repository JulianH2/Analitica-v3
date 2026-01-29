import sys
import os

# 1. Configuración de Django (Obligatorio para que no falle)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from django.conf import settings
if not settings.configured:
    settings.configure(BASE_DIR=BASE_DIR, DEBUG=True)
    import django
    django.setup()

# 2. Importamos los servicios
from services.data_manager import data_manager
from services.pbi_mapper import PBI_MAPPING

def run_full_audit():
    print("\n=======================================================")
    print(" 🕵️  AUDITORÍA COMPLETA DE MAPEO POWER BI")
    print("=======================================================\n")

    total_keys = 0
    mapped_keys = 0
    missing_keys = 0

    # Recorremos cada sección del mapa real
    for section, content in PBI_MAPPING.items():
        print(f"--- 📂 SECCIÓN: {section.upper()} ---")
        
        kpis = content.get('kpis', {})
        if not kpis:
            print("   (No hay KPIs definidos)")
            continue

        for kpi_key in kpis.keys():
            total_keys += 1
            # Le preguntamos al DataManager (simulando la app real)
            pbi_name = data_manager.get_pbi_measure_name(section, kpi_key)
            
            if pbi_name:
                print(f"   ✅ {kpi_key:<30} -> {pbi_name}")
                mapped_keys += 1
            else:
                print(f"   ❌ {kpi_key:<30} -> SIN MAPEO (None)")
                missing_keys += 1
        
        print("") # Espacio entre secciones

    # Resumen final
    print("=======================================================")
    print(f"📊 RESUMEN FINAL:")
    print(f"   Total Variables: {total_keys}")
    print(f"   Conectadas:      {mapped_keys}  ({(mapped_keys/total_keys)*100:.1f}%)")
    print(f"   Faltantes:       {missing_keys}  ({(missing_keys/total_keys)*100:.1f}%)")
    print("=======================================================")
    
    if missing_keys > 0:
        print("\n⚠️  ADVERTENCIA: Tienes variables sin conectar (marcadas con ❌).")
        print("    Estas devolverán '0' o datos simulados hasta que las arregles en 'pbi_mapper.py'.")
    else:
        print("\n🚀 ¡SISTEMA LISTO! Todo está mapeado al 100%.")

if __name__ == "__main__":
    run_full_audit()