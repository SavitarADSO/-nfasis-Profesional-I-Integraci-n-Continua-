"""
Contenedor 1 - API Flask.

Almacena y lee mensajes en la base de datos PostgreSQL (contenedor 2).

Punto clave de la rúbrica (paso 5): la conexión NO usa "localhost" ni una IP
fija. Usa el NOMBRE DEL SERVICIO de Docker Compose ("db"), que es la forma
correcta de resolver un contenedor dentro de la red compartida.
"""

import os
import time
from contextlib import contextmanager

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuración (variables de entorno inyectadas por docker-compose / .env)
# ---------------------------------------------------------------------------
DB_HOST = os.environ.get("DB_HOST", "db")  # "db" = nombre del servicio, NO localhost
DB_PORT = os.environ.get("DB_PORT", "5432")
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]


def get_conn():
    """Abre una conexión nueva a PostgreSQL usando el host por nombre de servicio."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        connect_timeout=5,
    )


@contextmanager
def conexion():
    """Context manager: commit/rollback automático y cierre de la conexión."""
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                yield cur
    finally:
        conn.close()


def esperar_base_datos(intentos=30, espera=2):
    """Reintenta la conexión hasta que PostgreSQL acepte consultas."""
    for i in range(intentos):
        try:
            conn = get_conn()
            conn.close()
            print(f"[init] Base de datos disponible en {i + 1} intento(s).", flush=True)
            return True
        except psycopg2.OperationalError as exc:
            print(f"[init] BD no lista ({i + 1}/{intentos}): {exc}", flush=True)
            time.sleep(espera)
    return False


def init_db():
    """Crea la tabla mensajes si aún no existe."""
    with conexion() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mensajes (
                id     SERIAL PRIMARY KEY,
                texto  TEXT NOT NULL,
                creado TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


# ---------------------------------------------------------------------------
# Rutas de la API
# ---------------------------------------------------------------------------
@app.get("/")
def health():
    """Endpoint de salud: comprueba que la app alcanza a la base de datos."""
    estado_db = "desconocido"
    try:
        with conexion() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        estado_db = "ok"
    except psycopg2.Error as exc:
        estado_db = f"error: {exc}"

    return jsonify(
        status="ok",
        servicio="app",
        db_host=DB_HOST,
        db_estado=estado_db,
    )


@app.post("/mensajes")
def crear_mensaje():
    """Guarda un mensaje en PostgreSQL (app -> db)."""
    datos = request.get_json(silent=True) or {}
    texto = (datos.get("texto") or "").strip()
    if not texto:
        return jsonify(error="El campo 'texto' es obligatorio"), 400

    with conexion() as cur:
        cur.execute(
            "INSERT INTO mensajes (texto) VALUES (%s) RETURNING id, texto", (texto,)
        )
        nuevo_id, texto_guardado = cur.fetchone()

    return jsonify(id=nuevo_id, texto=texto_guardado), 201


@app.get("/mensajes")
def listar_mensajes():
    """Devuelve todos los mensajes almacenados en PostgreSQL (db -> app)."""
    with conexion() as cur:
        cur.execute("SELECT id, texto FROM mensajes ORDER BY id")
        filas = cur.fetchall()

    return jsonify([{"id": i, "texto": t} for i, t in filas])


@app.get("/mensajes/<int:mensaje_id>")
def obtener_mensaje(mensaje_id):
    """Devuelve un mensaje puntual por su identificador."""
    with conexion() as cur:
        cur.execute("SELECT id, texto FROM mensajes WHERE id = %s", (mensaje_id,))
        fila = cur.fetchone()

    if fila is None:
        return jsonify(error="Mensaje no encontrado"), 404

    return jsonify({"id": fila[0], "texto": fila[1]})


# ---------------------------------------------------------------------------
# Arranque
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if esperar_base_datos():
        init_db()
        print("[init] Tabla 'mensajes' verificada.", flush=True)
    else:
        print("[init] ERROR: la base de datos no respondió; se reintenta al reiniciar.", flush=True)

    # 0.0.0.0 es obligatorio para que el contenedor sea alcanzable desde fuera.
    app.run(host="0.0.0.0", port=5000)
