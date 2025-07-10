#!/usr/bin/env bash
# Generate Streamlit secrets.toml from environment variables
mkdir -p /app/.streamlit
cat <<EOF > /app/.streamlit/secrets.toml
[connections.postgresql]
dialect = "${POSTGRESQL_DIALECT}"
host = "${POSTGRESQL_HOST}"
port = "${POSTGRESQL_PORT}"
database = "${POSTGRESQL_DATABASE}"
user = "${POSTGRESQL_USERNAME}"
password = "${POSTGRESQL_PASSWORD}"
EOF

# Execute the Streamlit app
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0
