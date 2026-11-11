# Capturas de evidencia

En esta carpeta se guardan las capturas de pantalla de la ejecucion del proyecto,
una por cada evidencia listada abajo. Cada figura del informe referencia el
archivo correspondiente a traves del macro `\captura`, de modo que los nombres
deben respetarse exactamente.

| Archivo                     | Que debe mostrar                                              |
|-----------------------------|---------------------------------------------------------------|
| `01-git-log.png`            | `git log --oneline` con la secuencia de commits                |
| `02-docker-build.png`       | Salida de `docker compose build`                              |
| `03-docker-compose-up.png`  | Salida de `docker compose up -d` (red y volumen creados)      |
| `04-docker-ps.png`          | Salida de `docker ps` con `ci_app` y `ci_db` en Up             |
| `05-network-inspect.png`    | Salida de `docker network inspect <red>`                      |
| `06-curl-post.png`          | `POST /mensajes` devolviendo `201` con el `id`                 |
| `07-curl-get.png`           | `GET /mensajes` devolviendo el mensaje insertado              |
| `08-dns-db.png`             | `socket.gethostbyname('db')` desde dentro del contenedor app  |
| `09-psql-select.png`        | `SELECT * FROM mensajes;` ejecutado en PostgreSQL             |
| `10-actions-verde.png`      | Ejecucion del pipeline en verde en la pestaña Actions de GitHub|
| `10-logs.png`               | Logs de arranque del contenedor `app`                         |

Si falta alguna imagen, el informe muestra un recuadro que indica el nombre
exacto del archivo pendiente y sigue compilando sin errores.
