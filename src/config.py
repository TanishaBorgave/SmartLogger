
SEVERITY_MAP = {
    "DEBUG": 0,
    "INFO": 1,
    "WARN": 2,
    "ERROR": 3,
    "CRITICAL": 4
}

MODULES = [
    "APIGateway",
    "AuthService",
    "DatabaseService",
    "SystemService"
]


EVENT_TYPES = {

    "APIGateway": {

        "REQUEST_OK": {
            "severity": "INFO",
            "weight": 50,
            "message": "API request completed successfully",
            "value_range": (100, 500)
        },

        "REQUEST_CREATED": {
            "severity": "INFO",
            "weight": 25,
            "message": "API resource created successfully",
            "value_range": (100, 500)
        },

        "REQUEST_BAD": {
            "severity": "WARN",
            "weight": 8,
            "message": "API request contained invalid data",
            "value_range": None
        },

        "REQUEST_TIMEOUT": {
            "severity": "ERROR",
            "weight": 2,
            "message": "API request timed out",
            "value_range": (1000, 5000)
        },

        "HIGH_LATENCY": {
            "severity": [
                (100, "INFO"),
                (200, "WARN"),
                (500, "ERROR"),
                (float("inf"), "CRITICAL")
            ],
            "weight": 3,
            "message": "API request latency exceeded expected threshold",
            "value_range": (20, 500)
        }
    },

    "AuthService": {

        "AUTH_SUCCESS": {
            "severity": "INFO",
            "weight": 45,
            "message": "User authentication successful",
            "value_range": None
        },

        "TOKEN_ISSUED": {
            "severity": "INFO",
            "weight": 30,
            "message": "Authentication token issued",
            "value_range": None
        },

        "AUTH_FAILURE": {
            "severity": "WARN",
            "weight": 8,
            "message": "User authentication failed",
            "value_range": None
        },

        "TOKEN_EXPIRED": {
            "severity": "WARN",
            "weight": 5,
            "message": "Authentication token expired",
            "value_range": None
        },

        "AUTH_SERVICE_ERROR": {
            "severity": "ERROR",
            "weight": 2,
            "message": "Authentication service encountered an error",
            "value_range": None
        }
    },

    "DatabaseService": {

        "REQUEST_OK": {
            "severity": "INFO",
            "weight": 45,
            "message": "Database request completed successfully",
            "value_range": (20, 100)
        },

        "QUERY_EXECUTED": {
            "severity": "INFO",
            "weight": 30,
            "message": "Database query executed successfully",
            "value_range": (20, 100)
        },

        "DB_SLOW_QUERY": {
            "severity": [
                (100, "INFO"),
                (200, "WARN"),
                (500, "ERROR"),
                (float("inf"), "CRITICAL")
            ],
            "weight": 5,
            "message": "Query exceeded expected latency",
            "value_range": (80, 500)
        },

        "DB_CONN_LOST": {
            "severity": "ERROR",
            "weight": 2,
            "message": "Connection to primary database lost",
            "value_range": None
        },

        "DB_CONNECTION_RESTORED": {
            "severity": "INFO",
            "weight": 2,
            "message": "Database connection restored",
            "value_range": None
        }
    },

    "SystemService": {

        "SERVICE_STARTED": {
            "severity": "INFO",
            "weight": 30,
            "message": "System service started successfully",
            "value_range": None
        },

        "HEALTH_CHECK_OK": {
            "severity": "INFO",
            "weight": 45,
            "message": "System health check passed",
            "value_range": None
        },

        "HIGH_CPU": {
            "severity": [
                (60, "INFO"),
                (80, "WARN"),
                (95, "ERROR"),
                (float("inf"), "CRITICAL")
            ],
            "weight": 4,
            "message": "CPU utilization exceeded expected level",
            "value_range": (20, 100)
        },

        "HIGH_MEMORY": {
            "severity": [
                (60, "INFO"),
                (80, "WARN"),
                (95, "ERROR"),
                (float("inf"), "CRITICAL")
            ],
            "weight": 4,
            "message": "Memory utilization exceeded expected level",
            "value_range": (20, 100)
        },

        "SERVICE_ERROR": {
            "severity": "ERROR",
            "weight": 2,
            "message": "System service encountered an error",
            "value_range": None
        }
    }
}