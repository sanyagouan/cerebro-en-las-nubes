import os
import requests
import sys

def check_dashboard():
    print("--- INICIANDO PROTOCOLO DE VALIDACIÓN ---")
    
    # 1. Verificar Archivo
    file_path = r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY\dashboard.html"
    if not os.path.exists(file_path):
        print(f"[FAIL] El archivo no existe: {file_path}")
        return False
    else:
        size = os.path.getsize(file_path)
        print(f"[PASS] Archivo encontrado. Tamaño: {size} bytes")

    # 2. Verificar Conectividad a CDNs (Tailwind, Chart.js)
    cdns = [
        "https://cdn.tailwindcss.com",
        "https://cdn.jsdelivr.net/npm/chart.js",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ]
    
    all_cdns_ok = True
    print("\n--- VERIFICANDO RECURSOS EXTERNOS (CDNs) ---")
    for url in cdns:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                print(f"[PASS] Conexión establecida: {url}")
            else:
                print(f"[WARN] Respuesta inusual ({response.status_code}): {url}")
        except Exception as e:
            print(f"[FAIL] No se puede conectar a: {url}. Error: {e}")
            all_cdns_ok = False
    
    if not all_cdns_ok:
        print("\n[CRITICAL] Hay problemas de conexión con las librerías gráficas.")
        print("El dashboard se verá incompleto o blanco.")
        return False
        
    print("\n[SUCCESS] Validación completada. El sistema está listo para visualizarse.")
    return True

if __name__ == "__main__":
    if check_dashboard():
        sys.exit(0)
    else:
        sys.exit(1)
