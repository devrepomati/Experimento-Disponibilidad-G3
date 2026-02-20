#!/bin/bash
# Script para crear un endpoint mock en WireMock con lógica condicional

set -e

MAPPINGS_DIR="./wiremock/mappings"
mkdir -p "$MAPPINGS_DIR"

# Caso 1: should_fail=true -> ERROR
cat > "$MAPPINGS_DIR/pay-mock-fail.json" <<'EOF'
{
  "request": {
    "method": "POST",
    "url": "/api/pay",
    "bodyPatterns": [
      {
        "matchesJsonPath": "$[?(@.should_fail == true || @.should_fail == 'true' || @.should_fail == 'True')]"
      }
    ],
    "headers": {
      "Content-Type": {
        "contains": "application/json"
      }
    }
  },
  "response": {
    "status": 400,
    "jsonBody": {
      "error": "ERROR"
    },
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
EOF

# Caso 2: cualquier otro -> status: pay
cat > "$MAPPINGS_DIR/pay-mock-success.json" <<'EOF'
{
  "request": {
    "method": "POST",
    "url": "/api/pay",
    "bodyPatterns": [
      {
        "matchesJsonPath": "$[?(!(@.should_fail == true || @.should_fail == 'true' || @.should_fail == 'True'))]"
      }
    ],
    "headers": {
      "Content-Type": {
        "contains": "application/json"
      }
    }
  },
  "response": {
    "status": 200,
    "jsonBody": {
      "status": "pay"
    },
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
EOF

echo "Mocks creados:"
echo "POST /api/pay con should_fail=true -> 400 { error: 'ERROR' }"
echo "POST /api/pay (otros casos) -> 200 { status: 'pay' }"