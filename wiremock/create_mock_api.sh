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

# Mock para /api/price-strategy3
cat > "$MAPPINGS_DIR/price-strategy3-mock.json" <<'EOF'
{
  "request": {
    "method": "POST",
    "url": "/api/price-strategy3",
    "bodyPatterns": [
      {
        "matchesJsonPath": "$[?(@.fail_strategy3 == true || @.fail_strategy3 == 'true' || @.fail_strategy3 == 'True')]"
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

cat > "$MAPPINGS_DIR/price-strategy3-mock-success.json" <<'EOF'
{
  "request": {
    "method": "POST",
    "url": "/api/price-strategy3",
    "headers": {
      "Content-Type": {
        "contains": "application/json"
      }
    }
  },
  "response": {
    "status": 200,
    "jsonBody": {
      "price": "{{jsonPath request.body '$.base' multiply 1.10 add 5 round 2}}"
    },
    "headers": {
      "Content-Type": "application/json"
    },
    "transformers": ["response-template"]
  }
}
EOF

echo "Mocks creados:"
echo "POST /api/pay con should_fail=true -> 400 { error: 'ERROR' }"
echo "POST /api/pay (otros casos) -> 200 { status: 'pay' }"
echo "POST /api/price-strategy3 con fail_strategy3=true -> 400 { error: 'ERROR' }"
echo "POST /api/price-strategy3 (otros casos) -> 200 { result: 'ok' }"
