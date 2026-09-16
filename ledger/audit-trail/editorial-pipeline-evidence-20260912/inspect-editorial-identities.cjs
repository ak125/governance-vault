// Read-only evidence probe. Uses the native TypeScript mapper without constructing a writer.
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const app = '/opt/automecanik/app/.claude/worktrees/editorial-pipeline-20260912';
process.env.TS_NODE_PROJECT = path.join(app, 'backend/tsconfig.json');
require(path.join(app,'node_modules/ts-node')).register({transpileOnly:true});
require(path.join(app,'node_modules/tsconfig-paths/register'));
const {mapExportBlockToDbBlock: map} = require(path.join(app,'backend/src/modules/seo-projection/seo-projection-writer.service.ts'));
const input = JSON.parse(fs.readFileSync(path.join(__dirname,'editorial-identity-inputs.json'),'utf8'));
const nonEntityIndexes=input.errors.filter(e=>e.path.endsWith('/proposals/_index.md'));
const result={heads:input.heads,files_read:input.inputs.length,excluded:[...(input.excluded??[]),...nonEntityIndexes.map(e=>({path:e.path,reason:'navigation index without entity frontmatter; inspected explicitly'}))],errors:input.errors.filter(e=>!e.path.endsWith('/proposals/_index.md')),counts:{},countsByRoot:{},mapped:[],mapperSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(app,'backend/src/modules/seo-projection/seo-projection-writer.service.ts'))).digest('hex'),collisions:[],identicalContentDifferentIds:[],sameSectionDifferentRoles:[]};
for (const rec of input.records) {
 const {payload:p,...meta}=rec;
 const c=result.counts[meta.stage]??={documents:0,blocks:0}; c.documents++;
 const root=Object.keys(input.heads).find(r=>meta.path.startsWith(r+'/'));
 const rc=(result.countsByRoot[root]??={})[meta.stage]??={documents:0,blocks:0}; rc.documents++;
 const groups=new Map(), contents=new Map(), sections=new Map();
 try { for (const [index,b] of (p.blocks??[]).entries()) {
  c.blocks++; rc.blocks++;
  const row=map(p.entity_id,b,index);
  const summary={index,role:b.role,section:b.section??null,usefulness_target:b.usefulness_target??null,blockId:row.blockId,contentHash:row.contentHash,textHash:crypto.createHash('sha256').update(b.content_md??'').digest('hex')};
  result.mapped.push({...meta,entity_id:p.entity_id,...summary});
  for(const [m,k] of [[groups,row.blockId],[contents,b.role+'|'+summary.textHash],[sections,row.blockKind]]) {if(!m.has(k))m.set(k,[]);m.get(k).push(summary);}
 }
 for(const [blockId,blocks]of groups) if(blocks.length>1) result.collisions.push({...meta,entity_id:p.entity_id,blockId,classification:new Set(blocks.map(b=>b.textHash)).size===1?'same-text':'different-text',blocks});
 for(const blocks of contents.values())if(blocks.length>1&&new Set(blocks.map(b=>b.blockId)).size>1)result.identicalContentDifferentIds.push({...meta,entity_id:p.entity_id,blocks});
 for(const blocks of sections.values())if(blocks.length>1&&new Set(blocks.map(b=>b.role)).size>1)result.sameSectionDifferentRoles.push({...meta,entity_id:p.entity_id,blocks});
 } catch(e){result.errors.push({...meta,error:String(e)});}
}
fs.writeFileSync(path.join(__dirname,process.argv[2]||'editorial-identity-corpus.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({counts:result.counts,collisions:result.collisions.length,identicalContentDifferentIds:result.identicalContentDifferentIds.length,sameSectionDifferentRoles:result.sameSectionDifferentRoles.length,errors:result.errors},null,2));
