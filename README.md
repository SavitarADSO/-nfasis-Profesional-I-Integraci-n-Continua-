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
├── jenkins/
│   └── Dockerfile          # Jenkins con Docker CLI para ejecutar el pipeline
├── Jenkinsfile             # Pipeline de Jenkins (Entrega 2)
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

## 6. Jenkins (Entrega 2)

Jenkins se ejecuta como un tercer servicio de Compose en la misma red. Su volumen
`jenkins_home` conserva la configuración y los trabajos. El puerto web se publica
solo en el equipo local (`http://localhost:8080`).

```powershell
# Con Docker Desktop iniciado y el archivo .env ya creado
docker compose up -d --build
docker compose ps
docker compose logs -f jenkins

# Contraseña de desbloqueo del primer inicio
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

En el asistente web, desbloquee Jenkins, instale los plugins sugeridos y cree
un usuario administrador. Después cree un elemento de tipo **Pipeline**:

1. En **Pipeline**, elija **Pipeline script from SCM** y **Git**.
2. Use la URL de este repositorio, la rama `*/main` y `Jenkinsfile` como ruta.
   Al ser público, no necesita credenciales.
3. En **Build Triggers**, active **Poll SCM** con `H/5 * * * *`.
4. Guarde y seleccione **Build Now**. Las etapas construyen la imagen de Flask
   y comprueban que `app.py` compila dentro del contenedor.

> La imagen de Jenkins usa el socket de Docker del equipo para construir
> imágenes. Esto concede a Jenkins control sobre el motor Docker y se limita
> aquí a un entorno académico local; no es una configuración para exponer en
> una red pública.

El informe y la lista de capturas de la Entrega 2 están en `docs/`.

---

## 7. Comandos útiles

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

## 8. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `could not translate host name "db"` | El contenedor `app` no está en la red de Compose o `DB_HOST` quedó como `localhost` | Verifique `docker network inspect` y `docker compose exec app env \| grep DB_HOST` |
| `password authentication failed for user` | La contraseña del `.env` no coincide con la guardada en el volumen | `docker compose down -v` y vuelva a levantar |
| La app reinicia en bucle al arrancar | PostgreSQL todavía no está listo | `depends_on` con `condition: service_healthy` ya lo cubre; si persiste, `docker compose logs app` |
| `port is already allocated` | El puerto 5000 ya está ocupado | `netstat -ano \| findstr :5000` y libere el proceso |

---

## 9. Informes

Los informes de ambas entregas están en `docs/` como fuentes LaTeX y PDF. Se
compilan con [Tectonic](https://tectonic-typesetting.github.io/) o en
[Overleaf](https://www.overleaf.com/). Por ejemplo:

```bash
cd docs
tectonic informe_entrega1.tex
tectonic informe_entrega2.tex
```

Las capturas se guardan en las carpetas indicadas por cada informe. Si falta alguna,
el documento muestra un recuadro de "captura pendiente" y compila igualmente.
