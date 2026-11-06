'use strict';
const test=require('node:test');const assert=require('node:assert/strict');
const {buildDependencyGraph,buildReverseDependencyGraph,toDot}=require('../src/graph');
test('BFS traverses transitively and visits a cycle once',async()=>{const r={A:['B','C'],B:['D'],C:['D','E'],D:['A'],E:[]};const g=await buildDependencyGraph({root:'A',maxDepth:3,getDependencies:async n=>r[n]});assert.equal(g.nodes.length,5);assert.equal(g.edges.length,6)});
test('max depth zero does not expand root',async()=>{const g=await buildDependencyGraph({root:'A',maxDepth:0,getDependencies:async()=>['B']});assert.equal(g.nodes.length,1);assert.equal(g.edges.length,0)});
test('reverse BFS returns direct and transitive dependents',async()=>{const r={A:['B'],B:['C'],C:[],D:['C'],E:['D']};const g=await buildReverseDependencyGraph({target:'C',getAllDependencies:async()=>r});assert.deepEqual(g.nodes.map(x=>x.name),['C','B','D','A','E']);assert.equal(g.edges.length,4)});
test('DOT output includes directed edges',()=>{const d=toDot({root:'A',nodes:[{name:'A'},{name:'B'}],edges:[{from:'A',to:'B'}]});assert.match(d,/'A'|"A"/);assert.match(d,/->/)});
