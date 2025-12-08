apt-get update -y
apt-get upgrade -y
echo "=== REFRESHING END ==="

apt install python3.10-venv
apt install libicu-dev python3-icu pkg-config libpq-dev libsqlite3-dev

python3.10 -m venv ../../.pai_venv
source ../../.pai_venv/bin/activate
echo "=== ENV-CREATION END ==="

pip install -r requirements.txt

echo "=== PACKAGES-INSTALLATION END"
