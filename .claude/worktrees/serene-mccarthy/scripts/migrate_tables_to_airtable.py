"""
Script de migración: Mesas hardcoded → Airtable.
Migra las 23 mesas definidas en table.py a Airtable MESAS.

EJECUCIÓN:
    python scripts/migrate_tables_to_airtable.py

NOTAS:
- Requiere Airtable MCP configurado
- Limpia datos existentes antes de migrar
- Migra MESAS_TERRAZA + MESAS_INTERIOR + MESAS_AUXILIARES
"""
import asyncio
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.entities.table import ALL_MESAS
from src.infrastructure.repositories.table_repository import table_repository
from src.core.entities.table import Table
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def clear_existing_tables():
    """Limpia todas las mesas existentes en Airtable."""
    logger.info("🗑️  Limpiando mesas existentes en Airtable...")

    try:
        existing_tables = await table_repository.list_all()

        for table in existing_tables:
            await table_repository.delete(table.id)
            logger.info(f"  ❌ Eliminada: {table.id} - {table.nombre}")

        logger.info(f"✅ Limpiadas {len(existing_tables)} mesas existentes\n")

    except Exception as e:
        logger.error(f"Error limpiando mesas: {e}")
        raise


async def migrate_hardcoded_tables():
    """Migra las 23 mesas hardcoded a Airtable."""
    logger.info(f"📦 Migrando {len(ALL_MESAS)} mesas hardcoded a Airtable...\n")

    migrated = 0
    failed = 0

    for mesa_dict in ALL_MESAS:
        try:
            # Crear objeto Table
            table = Table(**mesa_dict)

            # Crear en Airtable
            await table_repository.create(table)

            logger.info(f"  ✅ {table.id:8s} | {table.nombre:20s} | {table.zona:8s} | Cap: {table.capacidad_max}")
            migrated += 1

        except Exception as e:
            logger.error(f"  ❌ Error migrando {mesa_dict.get('id', 'UNKNOWN')}: {e}")
            failed += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Migración completada:")
    logger.info(f"   - Migradas: {migrated}")
    logger.info(f"   - Fallidas: {failed}")
    logger.info(f"{'='*60}\n")


async def verify_migration():
    """Verifica que la migración fue exitosa."""
    logger.info("🔍 Verificando migración...\n")

    try:
        all_tables = await table_repository.list_all()

        # Agrupar por zona
        terraza = [t for t in all_tables if t.zona.value == "Terraza"]
        interior = [t for t in all_tables if t.zona.value == "Interior"]

        logger.info(f"📊 Resumen en Airtable:")
        logger.info(f"   - Terraza: {len(terraza)} mesas")
        logger.info(f"   - Interior: {len(interior)} mesas")
        logger.info(f"   - TOTAL: {len(all_tables)} mesas")

        # Verificar que coincide con hardcoded
        if len(all_tables) == len(ALL_MESAS):
            logger.info(f"\n✅ VERIFICACIÓN EXITOSA: {len(all_tables)} mesas migradas correctamente")
            return True
        else:
            logger.error(f"\n❌ ERROR: Expected {len(ALL_MESAS)}, got {len(all_tables)}")
            return False

    except Exception as e:
        logger.error(f"Error en verificación: {e}")
        return False


async def main():
    """Ejecuta migración completa."""
    logger.info("\n" + "="*60)
    logger.info("🚀 MIGRACIÓN DE MESAS: Hardcoded → Airtable")
    logger.info("="*60 + "\n")

    try:
        # Paso 1: Limpiar
        await clear_existing_tables()

        # Paso 2: Migrar
        await migrate_hardcoded_tables()

        # Paso 3: Verificar
        success = await verify_migration()

        if success:
            logger.info("\n🎉 MIGRACIÓN COMPLETADA CON ÉXITO\n")
            return 0
        else:
            logger.error("\n❌ MIGRACIÓN COMPLETADA CON ERRORES\n")
            return 1

    except Exception as e:
        logger.error(f"\n💥 ERROR CRÍTICO EN MIGRACIÓN: {e}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
