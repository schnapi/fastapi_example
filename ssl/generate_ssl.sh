#!/bin/bash

# Script to generate a self-signed SSL certificate for localhost

# Output filenames
CERT_FILE="ssl/localhost.crt"
KEY_FILE="ssl/localhost.key"

# Default certificate values
COUNTRY="US"
STATE="California"
LOCALITY="San Francisco"
ORG="MyOrganization"
ORG_UNIT="IT"
COMMON_NAME="localhost"
EMAIL="admin@localhost"

# Generate private key
openssl genrsa -out "$KEY_FILE" 2048

# Generate certificate signing request (CSR) with default values
openssl req -new -key "$KEY_FILE" -out localhost.csr -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORG/OU=$ORG_UNIT/CN=$COMMON_NAME/emailAddress=$EMAIL"

# Generate self-signed certificate (valid 1 year)
openssl x509 -req -days 365 -in localhost.csr -signkey "$KEY_FILE" -out "$CERT_FILE"

# Cleanup CSR file (optional)
rm localhost.csr

echo "Self-signed certificate created:"
echo "Certificate: $CERT_FILE"
echo "Private Key: $KEY_FILE"