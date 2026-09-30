-- Read-only queries executed through the Supabase connector. No document bodies selected.
select table_name,column_name,data_type from information_schema.columns
where table_schema='public' and table_name in ('__seo_entity_fact_versions','__seo_entity_facts','__seo_entity_block_versions','__seo_entity_blocks','__rag_knowledge')
and column_name in ('entity_id','version_id','active_version_id','status','valid_to','content_hash','source_path','retrievable','content','id','created_at') order by table_name,ordinal_position;
select status,retrievable,count(*) from public.__rag_knowledge group by status,retrievable order by status,retrievable;
select (select count(*) from public.__seo_entity_facts) entities,(select count(*) from public.__seo_entity_fact_versions) fact_versions,
count(*) filter(where nullif(btrim(content),'') is null) empty_rag_bodies,count(*) filter(where retrievable is true) retrievable_rag_rows from public.__rag_knowledge;
select (select count(*) from public.__seo_content_blocks) blocks,(select count(*) from public.__seo_content_block_versions) block_versions,(select count(*) from public.__seo_projection_runs) projection_runs;
select id,status,content_hash,retrievable from public.__rag_knowledge where retrievable is true and status in ('merged','superseded') order by status,id;
