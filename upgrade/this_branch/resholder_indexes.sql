ALTER TABLE resholder ADD CONSTRAINT resholder_host_uk UNIQUE (host_id);
ALTER TABLE resholder ADD CONSTRAINT resholder_cluster_uk UNIQUE (cluster_id);

QUIT;
