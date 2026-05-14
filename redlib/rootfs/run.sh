#!/usr/bin/bashio

JSONSOURCE="/data/options.json"
mapfile -t arr < <(jq -r 'keys[]' "${JSONSOURCE}")
for KEY in "${arr[@]}"; do
    if bashio::config.has_value "$KEY"; then
        VALUE=$(bashio::config "$KEY")
        export "$KEY=$VALUE"
    fi
done

exec redlib
