#!/bin/sh

set -eu

SSH_SOURCE_DIR="${SSH_SOURCE_DIR:-/root/.ssh}"
SSH_TEMP_DIR="${SSH_TEMP_DIR:-/root/.ssh-temp}"

# Copiar SSH a ubicación temporal
mkdir -p "$SSH_TEMP_DIR"

if [ -d "$SSH_SOURCE_DIR" ]; then
	cp -R "$SSH_SOURCE_DIR"/. "$SSH_TEMP_DIR"/
fi

touch "$SSH_TEMP_DIR/config"
chmod 700 "$SSH_TEMP_DIR"
chmod 600 "$SSH_TEMP_DIR"/* 2>/dev/null || true

# Reescribir rutas ~/.ssh/ y rutas absolutas del directorio fuente hacia el temporal
sed -i \
	-e "s|~/.ssh/|${SSH_TEMP_DIR}/|g" \
	-e "s|${SSH_SOURCE_DIR}/|${SSH_TEMP_DIR}/|g" \
	"$SSH_TEMP_DIR/config"

export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -o BatchMode=yes -F ${SSH_TEMP_DIR}/config"

if [ "$#" -eq 0 ]; then
	set -- backup
fi

case "$1" in
	backup|migrate)
		set -- python app.py "$1"
		;;
	python|sh|bash)
		;;
	*)
		echo "Uso: docker run <imagen> [backup|migrate]"
		exit 1
		;;
esac

"$@"
EXIT_CODE=$?

# Si se proporcionaron PUID/PGID, asegurar que el directorio de backups pertenezca a ese usuario
TARGET_BACKUP_DIR="${BACKUP_DIR:-/app/backups}"
if [ -n "${PUID:-}" ] && [ -n "${PGID:-}" ] && [ -d "$TARGET_BACKUP_DIR" ]; then
	chown -R "${PUID}:${PGID}" "$TARGET_BACKUP_DIR" || true
fi

exit $EXIT_CODE