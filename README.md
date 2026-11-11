# proyecto-ci

Proyecto de Continuous Integration / Continuous Delivery con **Docker**, **Docker Compose** y
**GitHub Actions**.

Una API Flask (contenedor `app`) guarda y lee mensajes en una base de datos PostgreSQL
(contenedor `db`). Los dos contenedores se levantan juntos con `docker compose up` y se
comunican a través de la red propia de Compose usando el **nombre del servicio** (`db`).

---

## 1. Estructura del repositorio

```
proyecto-ci/
├── app/
│   ├── app.py              # API Flask (contenedor 1)
│   ├── requirements.txt    # Dependencias fijadas con pin de versión
│   ├── Dockerfile          # Imagen de la app (versión fija de Python)
│   └── .dockerignore       # Excluye archivos del contexto de build
├── .github/
│   └── workflows/
│       └── docker.yml      # Pipeline de GitHub Actions (paso 7)
├── docker-compose.yml      # Orquestación de los dos contenedores (paso 3)
├── .env.example            # Plantilla de variables de entorno (sí se sube)
├── .gitignore              # Ignora .env, __pycache__, etc.
├── README.md
└── docs/                   # Informe final en LaTeX (paso 8)
```

---

## 2. Requisitos

- Docker Desktop (Windows/Mac/Linux) con el plugin **Docker Compose v2**.
- Verificación: `docker --version` y `docker compose version`.

---

## 3. Puesta en marcha

### 3.1 Crear el archivo de variables de entorno

```bash
# Windows (PowerShell / CMD)
copy .env.example .env

# Linux / macOS / WSL
cp .env.example .env
```

Edite `.env` y ponga una contraseña real:

```env
POSTGRES_DB=proyecto
POSTGRES_USER=usuario
POSTGRES_PASSWORD=una_clave_real_y_unica
```

> `.env` está en `.gitignore`, por lo que **nunca** se sube al repositorio.
> `.env.example` sí se sube: es la plantilla que documenta qué variables existen.

### 3.2 Construir y levantar

```bash
docker compose build      # construye la imagen de la app
docker compose up -d      # levanta app y db en segundo plano
docker ps                 # ver los dos contenedores y su estado
```

### 3.3 Verificar la red creada por Compose

```bash
docker network ls
docker network inspect proyecto-ci_red_proyecto
```

El nombre real de la red se compone de `<nombre-del-proyecto>_<nombre-de-la-red>`,
por eso puede aparecer como `proyecto-ci_red_proyecto` o `proyecto-ci_default`.

---

## 4. Pruebas de comunicación (paso 5)

### 4.1 Guardar un dato (app -> db)

```bash
curl -X POST http://localhost:5000/mensajes \
  -H "Content-Type: application/json" \
  -d "{\"texto\":\"hola\"}"
```

En **PowerShell** `curl` es un alias de `Invoke-WebRequest` y no funciona igual:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/mensajes `
  -ContentType "application/json" -Body '{"texto":"hola"}'
```

### 4.2 Leerlo (db -> app)

```bash
curl http://localhost:5000/mensajes
```

```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:5000/mensajes
```

### 4.3 Demostrar que la app resuelve `db` por nombre de servicio

```bash
docker compose exec app python -c "import socket; print(socket.gethostbyname('db'))"
```

### 4.4 Ver el dato directamente en PostgreSQL

```bash
docker compose exec db psql -U usuario -d proyecto -c "SELECT * FROM mensajes;"
```

### 4.5 Comprobar que la app se conectó al host correcto

```bash
docker compose exec app env | grep DB_HOST
# DB_HOST=db
```

---

## 5. Pipeline de integración continua (paso 7)

Archivo: `.github/workflows/docker.yml`.

Cada `push` o `pull_request` sobre `main` dispara:

1. Descarga el código del repositorio (`actions/checkout@v4`).
2. Crea un `.env` de prueba con `cp .env.example .env`.
3. Construye las imágenes con `docker compose build`.
4. Levanta los contenedores y prueba la comunicación con `curl`
   (`POST /mensajes` y `GET /mensajes`) más la resolución del host `db`.
5. Apaga y limpia todo con `docker compose down -v`.

El semáforo verde se ve en la pestaña **Actions** del repositorio en GitHub.

---

## 6. Comandos útiles

| Comando | Para qué sirve |
|---|---|
| `docker compose build` | Construye la imagen de la app |
| `docker compose up -d` | Levanta app y db en segundo plano |
| `docker compose ps` | Estado de los contenedores del proyecto |
| `docker compose logs -f app` | Sigue el log de la aplicación |
| `docker compose exec db psql -U usuario -d proyecto` | Consola psql |
| `docker compose down` | Detiene y elimina contenedores y red |
| `docker compose down -v` | Detiene todo **y borra el volumen** `db_data` |

> Si cambia la contraseña de `.env` después de haber levantado la base una vez,
> ejecute `docker compose down -v`: PostgreSQL conserva la contraseña original
> dentro del volumen.

---

## 7. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `could not translate host name "db"` | El contenedor `app` no está en la red de Compose o `DB_HOST` quedó como `localhost` | Verifique `docker network inspect` y `docker compose exec app env \| grep DB_HOST` |
| `password authentication failed for user` | La contraseña del `.env` no coincide con la guardada en el volumen | `docker compose down -v` y vuelva a levantar |
| La app reinicia en bucle al arrancar | PostgreSQL todavía no está listo | `depends_on` con `condition: service_healthy` ya lo cubre; si persiste, `docker compose logs app` |
| `port is already allocated` | El puerto 5000 ya está ocupado | `netstat -ano \| findstr :5000` y libere el proceso |

---

## 8. Informe final

El informe de la entrega 1 (paso 8) está en `docs/informe_entrega1.tex` y se compila
con [Tectonic](https://tectonic-typesetting.github.io/) o en
[Overleaf](https://www.overleaf.com/):

```bash
cd docs
tectonic informe_entrega1.tex
```

Las capturas de pantalla se guardan en `docs/figuras/` con los nombres indicados en el
propio informe; si falta alguna, el documento muestra un recuadro de "captura pendiente"
y compila igual.
