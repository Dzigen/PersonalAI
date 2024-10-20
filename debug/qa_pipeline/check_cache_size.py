import aerospike

config = {'hosts':[("aerospikelservice", 3000)]}
client = aerospike.client(config).connect()
print(client.info_all("sets"))

# 08.10.24
#{'BB9020013AC4202': (None, 'ns=test:set=dist:objects=2640557:tombstones=0:data_used_bytes=168995648:truncate_lut=0:sindexes=0:index_populating=false:truncating=false:default-read-touch-ttl-pct=0:default-ttl=0:disable-eviction=false:enable-index=false:stop-writes-count=0:stop-writes-size=0;ns=test:set=short_path:objects=35022:tombstones=0:data_used_bytes=2342656:truncate_lut=0:sindexes=0:index_populating=false:truncating=false:default-read-touch-ttl-pct=0:default-ttl=0:disable-eviction=false:enable-index=false:stop-writes-count=0:stop-writes-size=0;ns=test:set=bfs_short_path:objects=30357385:tombstones=0:data_used_bytes=1942872640:truncate_lut=0:sindexes=0:index_populating=false:truncating=false:default-read-touch-ttl-pct=0:default-ttl=0:disable-eviction=false:enable-index=false:stop-writes-count=0:stop-writes-size=0;ns=test:set=dijkstra_short_path:objects=4724:tombstones=0:data_used_bytes=377920:truncate_lut=0:sindexes=0:index_populating=false:truncating=false:default-read-touch-ttl-pct=0:default-ttl=0:disable-eviction=false:enable-index=false:stop-writes-count=0:stop-writes-size=0;\n')}
