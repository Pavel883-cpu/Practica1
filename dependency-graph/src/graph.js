'use strict';
async function buildDependencyGraph({root,maxDepth,getDependencies}){
 if(!Number.isInteger(maxDepth)||maxDepth<0)throw Error('maxDepth должен быть неотрицательным целым числом');
 const nodes=new Map([[root,{name:root,depth:0}]]),edges=[],visited=new Set([root]),queue=[{name:root,depth:0}];let cursor=0;
 while(cursor<queue.length){const cur=queue[cursor++];if(cur.depth>=maxDepth)continue;for(const dep of [...new Set(await getDependencies(cur.name))].sort()){edges.push({from:cur.name,to:dep});if(!nodes.has(dep))nodes.set(dep,{name:dep,depth:cur.depth+1});if(!visited.has(dep)){visited.add(dep);queue.push({name:dep,depth:cur.depth+1})}}}
 return {root,maxDepth,nodes:[...nodes.values()],edges};
}
async function buildReverseDependencyGraph({target,getAllDependencies}){
 const map=await getAllDependencies(),incoming=new Map();
 for(const [name,deps] of Object.entries(map))for(const dep of deps){if(!incoming.has(dep))incoming.set(dep,[]);incoming.get(dep).push(name)}
 const nodes=new Map([[target,{name:target,depth:0}]]),edges=[],seen=new Set([target]),queue=[target];let cursor=0;
 while(cursor<queue.length){const cur=queue[cursor++];for(const dependent of [...new Set(incoming.get(cur)||[])].sort()){edges.push({from:dependent,to:cur});if(!seen.has(dependent)){seen.add(dependent);nodes.set(dependent,{name:dependent,depth:nodes.get(cur).depth+1});queue.push(dependent)}}}
 return {root:target,maxDepth:Infinity,nodes:[...nodes.values()],edges};
}
function toDot(g){const q=s=>'"'+String(s).replaceAll('\\','\\\\').replaceAll('"','\\"')+'"';const a=['digraph Dependencies {','  rankdir=LR;','  node [shape=box, style=rounded];',`  ${q(g.root)} [style="rounded,filled", fillcolor="lightblue"];`];for(const n of g.nodes)a.push(`  ${q(n.name)};`);for(const e of g.edges)a.push(`  ${q(e.from)} -> ${q(e.to)};`);a.push('}');return a.join('\n')+'\n'}
function formatGraph(g){const m=new Map();for(const e of g.edges){if(!m.has(e.from))m.set(e.from,[]);m.get(e.from).push(e.to)}return [`Граф зависимостей: ${g.root}`,...g.nodes.map(n=>`${'  '.repeat(n.depth)}${n.name}${m.has(n.name)?' -> '+m.get(n.name).join(', '):''}`)].join('\n')}
module.exports={buildDependencyGraph,buildReverseDependencyGraph,toDot,formatGraph};
