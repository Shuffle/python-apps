openssl req -new -x509 -newkey rsa:2048 -sha256 \
            -days 3650 \
            -nodes \
            -out example.crt \
            -keyout example.key \
            -subj "/C=SI/ST=Ljubljana/L=Ljubljana/O=Security/OU=IT Department/CN=www.example.com"

openssl pkcs12 -inkey example.key -in example.crt -export -out example.pfx -password pass:"<your password>"

