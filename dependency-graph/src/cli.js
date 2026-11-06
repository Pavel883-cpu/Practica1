'use strict';
const path = require('node:path');
const DEFAULTS = Object.freeze({ package: '', repository: 'https://registry.npmjs.org', testMode: false, version: 'latest', output: 'dependencies.dot', maxDepth: 3, reverse: false });
function parseArgs(argv) {
  const config = { ...DEFAULTS };
  const flags = { '--package':'package','--repository':'repository','--version':'version','--output':'output','--max-depth':'maxDepth' };
  for (let i=0;i<argv.length;i++) {
    const arg=argv[i];
    if(arg==='--test-mode') config.testMode=true;
    else if(arg==='--reverse') config.reverse=true;
    else if(arg==='--help'||arg==='-h') config.help=true;
    else if(flags[arg]) { const value=argv[i+1]; if(value===undefined||value.startsWith('--')) throw new Error(`Для параметра ${arg} требуется значение`); config[flags[arg]]=flags[arg]==='maxDepth'?Number(value):value; i++; }
    else throw new Error(`Неизвестный параметр: ${arg}`);
  }
  return config;
}
function validateConfig(c) {
  const e=[];
  if(!c.package||!/^(?:@[a-z0-9._-]+\/)?[a-z0-9._-]+$/i.test(c.package)) e.push('--package обязателен и должен содержать корректное имя npm-пакета');
  if(!c.repository) e.push('--repository не может быть пустым');
  if(!c.testMode) { try { const u=new URL(c.repository); if(!['http:','https:'].includes(u.protocol)) throw Error(); } catch { e.push('--repository должен быть HTTP(S) URL'); } }
  if(!c.version||!/^[a-zA-Z0-9*._+~-]+$/.test(c.version)) e.push('--version должен содержать версию или dist-tag');
  if(!c.output||!c.output.trim()) e.push('--output не может быть пустым');
  if(!Number.isInteger(c.maxDepth)||c.maxDepth<0||c.maxDepth>100) e.push('--max-depth должен быть целым числом от 0 до 100');
  return e;
}
function printConfig(c) { for(const [k,v] of Object.entries({package:c.package,repository:c.repository,testMode:c.testMode,version:c.version,output:c.output,maxDepth:c.maxDepth,reverse:c.reverse})) console.log(`${k}=${v}`); }
function printHelp(){console.log('Использование: node src/index.js --package <имя> [--repository URL|файл] [--test-mode] [--version версия] [--output файл.dot] [--max-depth N] [--reverse]');}
module.exports={DEFAULTS,parseArgs,validateConfig,printConfig,printHelp};
