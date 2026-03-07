#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostico para validar hipotesis de errores en Redis.

HIPOTESIS:
1. Variable 'compressed' fuera de scope (NameError)
2. Constantes TCP socket no disponibles (AttributeError)
3. Comparacion cursor SCAN incorrecta

Ejecutar: python scripts/diagnose_redis.py
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_tcp_constants():
    """Verificar si las constantes TCP estan disponibles."""
    print("\n=== TEST 1: Constantes TCP ===")
    import socket
    
    constants = ["TCP_KEEPIDLE", "TCP_KEEPINTVL", "TCP_KEEPCNT"]
    all_available = True
    
    for const in constants:
        try:
            value = getattr(socket, const)
            print(f"  [OK] socket.{const} = {value}")
        except AttributeError as e:
            print(f"  [ERROR] socket.{const} NO DISPONIBLE: {e}")
            all_available = False
    
    if all_available:
        print("  RESULTADO: Todas las constantes TCP disponibles")
    else:
        print("  RESULTADO: [WARN] Algunas constantes TCP no disponibles (problema en Windows)")
        print("  RECOMENDACION: Agregar try/except con fallback")
    
    return all_available


def test_compressed_scope():
    """Verificar el error de scope con variable 'compressed'."""
    print("\n=== TEST 2: Scope de variable 'compressed' ===")
    
    # Simulacion del codigo problematico original
    compress_threshold = 1024
    
    def _set():
        """Funcion interna que define 'compressed'."""
        value = {"test": "data"}
        import json
        serialized = json.dumps(value)
        compressed = serialized  # En el codigo real se comprime
        return True
    
    # El codigo original intentaba acceder a 'compressed' aqui
    try:
        result = _set()
        # Esto causaria NameError en el codigo original:
        # logger.debug(f"compressed: {len(compressed) > compress_threshold}")
        
        # Simular el acceso a 'compressed' fuera del closure
        _ = compressed  # type: ignore
        print("  [ERROR] No se detecto el error (esto no deberia pasar)")
        return False
    except NameError as e:
        print(f"  [OK] ERROR CONFIRMADO: {e}")
        print("  DIAGNOSTICO: La variable 'compressed' NO es accesible fuera de _set()")
        print("  RECOMENDACION: Usar lista/dict mutable para capturar el valor")
        return True


def test_cursor_scan_logic():
    """Verificar la logica del cursor SCAN."""
    print("\n=== TEST 3: Logica de cursor SCAN ===")
    
    # El codigo original:
    # cursor = "0"
    # while cursor != 0:
    #     ...
    
    cursor_string = "0"
    cursor_int = 0
    
    print(f"  cursor = '0' (string)")
    print(f"  while cursor != 0 (comparar con int):")
    print(f"    '0' != 0 = {cursor_string != cursor_int}")
    
    if cursor_string != cursor_int:
        print("  [WARN] PROBLEMA: '0' (string) != 0 (int) es TRUE")
        print("  Esto hace que el while se ejecute, pero es confuso")
        print("  RECOMENDACION: Usar cursor = 0 (int) y do-while pattern")
        return False
    else:
        print("  [OK]")
        return True


def test_redis_import():
    """Verificar que redis-py se puede importar."""
    print("\n=== TEST 4: Import de redis-py ===")
    try:
        import redis
        print(f"  [OK] redis version: {redis.__version__}")
        
        # Verificar ConnectionPool
        from redis.connection import ConnectionPool
        print(f"  [OK] ConnectionPool disponible")
        
        # Verificar que from_url existe
        if hasattr(ConnectionPool, 'from_url'):
            print(f"  [OK] ConnectionPool.from_url() disponible")
        else:
            print(f"  [ERROR] ConnectionPool.from_url() NO disponible")
            return False
            
        return True
    except ImportError as e:
        print(f"  [ERROR] Error importando redis: {e}")
        return False


def test_redis_cache_init():
    """Intentar inicializar RedisCache para ver errores."""
    print("\n=== TEST 5: Inicializacion de RedisCache ===")
    try:
        # Sin REDIS_URL configurado
        os.environ.pop("REDIS_URL", None)
        
        from src.infrastructure.cache.redis_cache import RedisCache
        cache = RedisCache()
        
        if not cache.enabled:
            print("  [OK] Cache se inicializa correctamente (disabled sin REDIS_URL)")
            return True
        else:
            print("  [WARN] Cache habilitado sin REDIS_URL (inesperado)")
            return False
    except Exception as e:
        print(f"  [ERROR] Error inicializando RedisCache: {type(e).__name__}: {e}")
        return False


def main():
    print("=" * 60)
    print("DIAGNOSTICO DE REDIS - Validacion de Hipotesis")
    print("=" * 60)
    
    results = {
        "TCP Constants": test_tcp_constants(),
        "Compressed Scope": test_compressed_scope(),
        "Cursor SCAN Logic": test_cursor_scan_logic(),
        "Redis Import": test_redis_import(),
        "RedisCache Init": test_redis_cache_init(),
    }
    
    print("\n" + "=" * 60)
    print("RESUMEN DE DIAGNOSTICO")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "[OK]" if passed else "[PROBLEMA]"
        print(f"  {test_name}: {status}")
    
    print("\n" + "=" * 60)
    print("CONCLUSIONES")
    print("=" * 60)
    
    if not results["TCP Constants"]:
        print("""
  1. CONSTANTES TCP: Fallan en Windows/algunos entornos Docker.
     SOLUCION: Ya implementada con try/except en __init__.
""")
    
    if results["Compressed Scope"]:
        print("""
  2. VARIABLE COMPRESSED: Confirmado error de scope.
     SOLUCION: Ya implementada usando lista _was_compressed.
""")
    
    if not results["Cursor SCAN Logic"]:
        print("""
  3. CURSOR SCAN: Logica confusa con string vs int.
     SOLUCION: Ya implementada usando cursor=0 (int) + first_iteration flag.
""")
    
    print("\nDiagnostico completado.")
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
