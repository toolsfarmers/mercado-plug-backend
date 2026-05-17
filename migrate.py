"""
Script de migración manual: aplica cambios de esquema pendientes.
Ejecutar una sola vez: python migrate.py
"""
import sys, os
sys.path.append(os.path.dirname(__file__))

from app.database import engine
from sqlalchemy import text

migrations = [
    # Habilita extensión unaccent para búsqueda sin tildes
    "CREATE EXTENSION IF NOT EXISTS unaccent;",
    # Agrega el valor 'operator' al enum userrole (si no existe)
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_enum
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid
            WHERE pg_type.typname = 'userrole' AND pg_enum.enumlabel = 'operator'
        ) THEN
            ALTER TYPE userrole ADD VALUE 'operator' BEFORE 'admin';
        END IF;
    END$$;
    """,
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
    # Agrega commission_rate a stores (si no existe)
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='stores' AND column_name='commission_rate'
        ) THEN
            ALTER TABLE stores ADD COLUMN commission_rate NUMERIC(5,4) NOT NULL DEFAULT 0.04;
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
