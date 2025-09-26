#!/bin/bash
#
# Generates a Zabbix graph and sends it via Evolution API (WhatsApp)
#

[ $# -ne 8 ] && {
    echo "Usage: $0 {URL} {User} {Password} {Item} {WA_URL} {WA_TO} {WA_APIKEY}  {MSG}"
    exit 1;
}

# Extra parameters for the graphic
_from="now-2h"
_to="now"
_width="1024"
_height="220"
_type="0"
_profileIdx="web.item.graph.filter"

# mandatory parameters
_ZABBIX_BASE="${1}"
_ZABBIX_USER="${2}"
_ZABBIX_PASSWORD="${3}"
_ZABBIX_ITEM_ID="${4}"
_WA_URL="${5}"
_WA_TO="${6}"
_WA_APIKEY="${7}"
_WA_MSG="${8}"

# turn \n into line break
_WA_MSG=$(echo -e "$_WA_MSG")

# Temporary files
_GRAPHICAL_FILE="$(mktemp /tmp/graphic.XXXXXXXXXX)"
_COOKIES_FILE="$(mktemp /tmp/cookies.XXXXXXXXXX)"

# Full URL of graphic
_ZABBIX_CHART="$_ZABBIX_BASE/chart.php?from=$_from&to=$_to&itemids[0]=$_ZABBIX_ITEM_ID&type=$_type&profileIdx=$_profileIdx&width=$_width&height=$_height"

echo "## Login to Zabbix"
_RESULT=$(curl -s -g -L -X POST -c $_COOKIES_FILE -d "name=$_ZABBIX_USER&password=$_ZABBIX_PASSWORD&enter=Sign in" "$_ZABBIX_BASE/index.php")
_SESSION_ID=$(echo -e $_RESULT | grep -E -o -m 1 '(csrf_token: "[0-9a-z]{64})"' | cut -d\" -f2)

echo "## Download graphical file"
curl -s -g -L -X POST -b $_COOKIES_FILE "$_ZABBIX_CHART" -o $_GRAPHICAL_FILE

echo "## Encode image to Base64"
BASE64_IMAGE=$(base64 -w 0 "$_GRAPHICAL_FILE")

echo "## Prepare JSON payload"
JSON_PAYLOAD=$(cat <<EOF
{
    "number": "$_WA_TO",
    "mediatype": "image",
    "mimetype": "image/png",
    "caption": "$_WA_MSG",
    "media": "$BASE64_IMAGE",
    "fileName": "chart.png",
    "delay": 1200
}
EOF
)

echo "## Send via Evolution API (WhatsApp)"
RESULT=$(curl -s -X POST "$_WA_URL" \
    -H "Content-Type: application/json" \
    -H "apikey: $_WA_APIKEY" \
    -d "$JSON_PAYLOAD")

echo "## Result: $RESULT"

# Cleanup
rm -f "$_COOKIES_FILE" "$_GRAPHICAL_FILE"
