'use strict';
const fs=require('node:fs/promises');
async function loadTestRepository(file){let raw;try{raw=await fs.readFile(file,'utf8')}catch(e){throw Error(`Не удалось прочитать JSON-репозиторий: ${e.message}`)}
 let graph;try{graph=JSON.parse(raw)}catch{throw Error('Некорректный JSON')};
 if(!graph||Array.isArray(graph)||typeof graph!=='object')throw Error('Корень JSON должен быть объектом');
 for(const [name,deps] of Object.entries(graph)){if(!/^[A-Z]+$/.test(name))throw Error(`Имя ${name} должно состоять из заглавных латинских букв`);if(!Array.isArray(deps)||deps.some(x=>typeof x!=='string'||!/^[A-Z]+$/.test(x)))throw Error(`Некорректные зависимости пакета ${name}`)}
 return graph;
}
module.exports={loadTestRepository};
