"""
Script de migración manual: aplica cambios de esquema pendientes.
Ejecutar una sola vez: python migrate.py
"""
import sys, os
sys.path.append(os.path.dirname(__file__))

from app.database import engine
from sqlalchemy import text

migrations = [
    # Agrega location_id a users (si no existe)
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='users' AND column_name='location_id'
        ) THEN
            ALTER TABLE users
            ADD COLUMN location_id INTEGER REFERENCES locations(id) ON DELETE SET NULL;
        END IF;
    END$$;
    """,
    # Agrega whatsapp_number a products (si no existe)
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='products' AND column_name='whatsapp_number'
        ) THEN
            ALTER TABLE products ADD COLUMN whatsapp_number VARCHAR(30);
        END IF;
    END$$;
    """,
]

with engine.connect() as conn:
    for i, sql in enumerate(migrations, 1):
        print(f"  Aplicando migracion {i}...")
        conn.execute(text(sql))
    conn.commit()

print("[OK] Todas las migraciones aplicadas.")
