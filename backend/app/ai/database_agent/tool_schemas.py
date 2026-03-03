"""
Anthropic tool schemas for the MindBridge Database Agent.
Defines the 4 tools Claude can call during the agentic loop.
"""

TOOL_SCHEMAS = [
    {
        "name": "check_blocking",
        "description": (
            "Query pg_stat_activity to find slow, blocked, or blocking queries in PostgreSQL. "
            "Returns active sessions exceeding the specified duration threshold, along with "
            "which sessions are blocking others. Use this to diagnose performance issues, "
            "lock contention, or long-running transactions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "min_duration_ms": {
                    "type": "integer",
                    "description": (
                        "Only return sessions running longer than this many milliseconds. "
                        "Defaults to 1000 (1 second). Use lower values (e.g. 100) for "
                        "fine-grained investigation, higher values (e.g. 5000) to filter "
                        "noise in busy systems."
                    ),
                },
            },
            "required": [],
        },
    },
    {
        "name": "query_database",
        "description": (
            "Execute a safe SELECT query against the MindBridge PostgreSQL database. "
            "Only SELECT statements are permitted — INSERT, UPDATE, DELETE, DROP, and other "
            "DML/DDL are blocked. Always use parameterized placeholders ($1, $2, ...) for "
            "any user-supplied values to prevent SQL injection. Use this to retrieve patient "
            "data, aggregate statistics, or inspect database state."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": (
                        "The SELECT SQL statement to execute. Must begin with SELECT. "
                        "Use $1, $2, ... placeholders for any variable values. "
                        "Example: 'SELECT id, patient_name, risk_level FROM patients "
                        "WHERE risk_level = $1 ORDER BY id' "
                    ),
                },
                "params": {
                    "type": "array",
                    "items": {},
                    "description": (
                        "Ordered list of parameter values corresponding to $1, $2, ... "
                        "placeholders in the SQL. Example: ['HIGH'] for a query with "
                        "WHERE risk_level = $1. Omit or pass empty array if no placeholders."
                    ),
                },
            },
            "required": ["sql"],
        },
    },
    {
        "name": "create_view",
        "description": (
            "Create or replace a reusable PostgreSQL VIEW for common clinical queries. "
            "Views encapsulate complex query logic under a descriptive name, making it easy "
            "for clinicians and other tools to run the same query without knowing SQL internals. "
            "Use descriptive names that reflect clinical purpose, e.g. 'high_risk_patients', "
            "'patients_missing_medications', 'crisis_calls_last_30_days'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": (
                        "Name for the PostgreSQL view. Use lowercase with underscores. "
                        "Should describe what the view returns clinically. "
                        "Example: 'high_risk_missing_meds' or 'active_crisis_patients'."
                    ),
                },
                "sql": {
                    "type": "string",
                    "description": (
                        "The SELECT SQL statement that defines the view body. "
                        "Do not include CREATE VIEW — only the SELECT query. "
                        "Do not use parameterized placeholders ($1) — views must use "
                        "literal values or reference other tables/columns. "
                        "Example: 'SELECT id, patient_name, risk_level, medication_adherence "
                        "FROM patients WHERE risk_level = \\'HIGH\\' ORDER BY id'"
                    ),
                },
            },
            "required": ["name", "sql"],
        },
    },
    {
        "name": "run_cleanup",
        "description": (
            "Safely delete records from an allowlisted table with full audit logging. "
            "IMPORTANT: Always run with dry_run=true first to preview what will be deleted, "
            "then ask for explicit user confirmation before running with dry_run=false. "
            "Only the following tables are permitted: appointments, session_logs, "
            "temp_uploads, notification_queue. "
            "Deletions are irreversible — the audit log records every operation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "table": {
                    "type": "string",
                    "description": (
                        "Table to delete records from. Must be one of: "
                        "appointments, session_logs, temp_uploads, notification_queue. "
                        "Any other table name will be rejected."
                    ),
                },
                "condition": {
                    "type": "string",
                    "description": (
                        "SQL WHERE clause fragment (without the WHERE keyword) that "
                        "identifies records to delete. Use specific, time-bounded conditions. "
                        "Example: 'appointment_date < NOW() - INTERVAL \\'2 years\\'' "
                        "or 'created_at < NOW() - INTERVAL \\'90 days\\' AND status = \\'cancelled\\''"
                    ),
                },
                "dry_run": {
                    "type": "boolean",
                    "description": (
                        "If true (default), only preview the count of records that would be "
                        "deleted without actually deleting anything. Always set to true on "
                        "the first call. Only set to false after showing the dry_run preview "
                        "to the user and receiving explicit confirmation."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": (
                        "Human-readable reason for the cleanup operation, recorded in the "
                        "audit log. Example: 'Routine cleanup of appointment records older "
                        "than 2 years per data retention policy.'"
                    ),
                },
                "performed_by": {
                    "type": "string",
                    "description": "Name or identifier of the person/system requesting the cleanup.",
                },
            },
            "required": ["table", "condition"],
        },
    },
]
