
## in homeassistant
/start_ha.sh

# database
# in connectors
./cloud_sql_proxy -instances=hass-db-cuau97:us-west1:hass-db-sql-server=tcp:3306

## appdaemon
appdaemon -c ./config

## connectors
activate connectors_env
python3 xbee_connect_ha.py 

## in hass-cuauhtemoc-97
docker-compose up