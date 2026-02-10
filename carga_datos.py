#!/usr/bin/env python3
"""
Carga de datos FoodTrack vía pyodbc.
Carga: foodtrucks, products, locations (Parte 1 - Python)
Errores de inserción se registran en failed_orders (tabla auxiliar).
"""

import os
import sys
from pathlib import Path

import pandas as pd
import pyodbc

# Ruta a los CSV (relativa a este script)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
# Alternativa: datos en carpeta del módulo M2L1
DATA_DIR_ALT = BASE_DIR.parent / "1. Introducción a bases de datos y sublenguaje DDL"

def _get_conn_str():
    """Usa Driver 18 si existe, si no Driver 17 (evita error si solo está instalado el 17)."""
    drivers = [d for d in pyodbc.drivers() if "ODBC Driver" in d and "SQL Server" in d]
    driver = "ODBC Driver 18 for SQL Server" if "ODBC Driver 18 for SQL Server" in drivers else (
        "ODBC Driver 17 for SQL Server" if "ODBC Driver 17 for SQL Server" in drivers else None
    )
    if not driver:
        raise RuntimeError(
            "No se encontró ODBC Driver 18 ni 17 para SQL Server. "
            "Instala con: brew install msodbcsql18 (tras brew tap microsoft/mssql-release)"
        )
    base = (
        f"Driver={{{driver}}};"
        "Server=localhost,1433;"
        "Database=FoodTrack;"
        "UID=SA;"
        "PWD=YourStrong@Passw0rd;"
    )
    if "18" in driver:
        base += "TrustServerCertificate=yes;"
    return base


CONN_STR = None  # Se asigna al conectar


def get_data_dir():
    if DATA_DIR.exists():
        return DATA_DIR
    if DATA_DIR_ALT.exists():
        return DATA_DIR_ALT
    raise FileNotFoundError(
        f"No se encontró carpeta data. Crea {DATA_DIR} o usa {DATA_DIR_ALT}"
    )


def create_failed_orders_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'failed_orders')
        CREATE TABLE failed_orders (
            id INT IDENTITY(1,1) PRIMARY KEY,
            tabla NVARCHAR(100),
            datos NVARCHAR(MAX),
            error NVARCHAR(MAX),
            created_at DATETIME2 DEFAULT GETDATE()
        )
    """)
    conn.commit()
    cursor.close()


def load_table(conn, df, table: str, columns: list):
    cursor = conn.cursor()
    cols = ", ".join(f"[{c}]" for c in columns)
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO [{table}] ({cols}) VALUES ({placeholders})"
    for _, row in df.iterrows():
        try:
            cursor.execute(sql, tuple(row[c] for c in columns))
        except Exception as e:
            cursor.execute(
                "INSERT INTO failed_orders (tabla, datos, error) VALUES (?, ?, ?)",
                (table, str(row.to_dict()), str(e)),
            )
    conn.commit()
    cursor.close()


def main():
    data_dir = get_data_dir()
    conn_str = _get_conn_str()

    conn = pyodbc.connect(conn_str)
    conn.autocommit = False
    create_failed_orders_table(conn)

    tables = [
        ("foodtrucks.csv", "foodtrucks", ["foodtruck_id", "name", "cuisine_type", "city"]),
        ("products.csv", "products", ["product_id", "foodtruck_id", "name", "price", "stock"]),
        ("locations.csv", "locations", ["location_id", "foodtruck_id", "location_date", "zone"]),
    ]

    for csv_file, table, cols in tables:
        path = data_dir / csv_file
        if not path.exists():
            print(f"Archivo no encontrado: {path}", file=sys.stderr)
            continue
        df = pd.read_csv(path)
        load_table(conn, df, table, cols)
        print(f"Cargados {len(df)} registros en {table}")

    conn.close()
    print("Carga completada.")


if __name__ == "__main__":
    main()
