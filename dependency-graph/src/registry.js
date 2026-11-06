'use strict';
function normalizeRegistryUrl(repository){const u=new URL(repository);if(!['http:','https:'].includes(u.protocol))throw Error('Разрешены только HTTP(S) URL');return u.toString().replace(/\/$/,'');}
async function fetchPackageMetadata({packageName,version,repository='https://registry.npmjs.org',fetchImpl=globalThis.fetch}){
 if(typeof fetchImpl!=='function')throw Error('Требуется Node.js 18+ (global fetch)');
 const url=`${normalizeRegistryUrl(repository)}/${encodeURIComponent(packageName)}/${encodeURIComponent(version)}`;
 let r;try{r=await fetchImpl(url,{headers:{accept:'application/vnd.npm.install-v1+json'}})}catch(e){throw Error(`Не удалось подключиться к npm Registry: ${e.message}`)}
 if(r.status===404)throw Error(`Пакет или версия не найдены: ${packageName}@${version}`);
 if(!r.ok)throw Error(`npm Registry вернул HTTP ${r.status}`);
 const data=await r.json();if(!data||typeof data!=='object')throw Error('Некорректные метаданные npm');return data;
}
function extractDirectDependencies(m){return [...new Set([...Object.keys(m.dependencies||{}),...Object.keys(m.optionalDependencies||{})])].sort();}
module.exports={normalizeRegistryUrl,fetchPackageMetadata,extractDirectDependencies};
