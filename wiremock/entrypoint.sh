#!/bin/bash
# Entrypoint para WireMock: crea los mocks y arranca el servidor

set -e

# Crear los mocks
bash /home/wiremock/create_mock_api.sh

# Ejecutar WireMock (comando por defecto)
/docker-entrypoint.sh "$@"