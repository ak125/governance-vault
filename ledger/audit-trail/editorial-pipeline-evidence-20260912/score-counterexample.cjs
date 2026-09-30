// Read-only counterexample: actual scoring method; Nest/DB constructors stubbed.
const fs=require('fs'),vm=require('vm'),ts=require(process.argv[2]+'/node_modules/typescript');
const root=process.argv[2];
function load(path,deps={}){const mod={exports:{}};const js=ts.transpileModule(fs.readFileSync(root+'/'+path,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,experimentalDecorators:true}}).outputText;vm.runInNewContext(js,{exports:mod.exports,module:mod,require:name=>{if(name in deps)return deps[name];throw Error('Unexpected import '+name)},console});return mod.exports;}
const constants=load('backend/src/config/conseil-pack.constants.ts');
const sourceConstants=load('backend/src/config/source-provenance.constants.ts');
const provenance=load('backend/src/modules/blog/utils/source-provenance.util.ts',{'../../../config/source-provenance.constants':sourceConstants});
const html=load('backend/src/modules/blog/utils/html-normalize.utils.ts');
const {ConseilQualityScorerService:C}=load('backend/src/modules/admin/services/conseil-quality-scorer.service.ts',{'@nestjs/common':{Injectable:()=>x=>x,Logger:class{}},'@database/services/supabase-base.service':{SupabaseBaseService:class{}},'../../../config/conseil-pack.constants':constants,'../../blog/utils/source-provenance.util':provenance,'../../blog/utils/html-normalize.utils':html});
const scorer=new C();const text='<p>'+Array(60).fill('banane').join(' ')+'</p>';
console.log(JSON.stringify({scope:'scoreSection only; no DB, no publication',section:'S1',content:'banane repeated 60 times',sources:'not-a-source',result:scorer.scoreSection('S1',text,'not-a-source'),no_sources_result:scorer.scoreSection('S1',text,null)},null,2));
