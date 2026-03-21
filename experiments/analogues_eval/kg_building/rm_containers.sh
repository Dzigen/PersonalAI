#!/usr/bin/bash
CONTAINERS_POSTFIX=$1

EXISTING_CONTAINERS=$(docker container ls -q --filter name="^personalai_mmenschikov_analogues_kgbuild.*$CONTAINERS_POSTFIX$")

echo $EXISTING_CONTAINERS

echo "Stoping containers..."
docker container stop ${EXISTING_CONTAINERS}
echo "Done."

echo "Removing containers..."
docker container rm ${EXISTING_CONTAINERS}
echo "Done."
