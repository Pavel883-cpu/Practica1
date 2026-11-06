'use strict';
const test=require('node:test');const assert=require('node:assert/strict');
const {fetchPackageMetadata,extractDirectDependencies}=require('../src/registry');
test('fetches exact package version and extracts dependencies',async()=>{let requested='';const m=await fetchPackageMetadata({packageName:'demo',version:'1.2.3',fetchImpl:async url=>{requested=url;return{ok:true,status:200,json:async()=>({dependencies:{alpha:'^1'},optionalDependencies:{beta:'*'}})}}});assert.match(requested,/demo\/1\.2\.3$/);assert.deepEqual(extractDirectDependencies(m),['alpha','beta'])});
test('404 reports missing package or version',async()=>{await assert.rejects(()=>fetchPackageMetadata({packageName:'missing',version:'1',fetchImpl:async()=>({ok:false,status:404})}),/не найдены/)});
