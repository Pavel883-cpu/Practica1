'use strict';
const test=require('node:test');const assert=require('node:assert/strict');
const {parseArgs,validateConfig}=require('../src/cli');
test('parses options',()=>{const c=parseArgs(['--package','A','--test-mode','--repository','r.json','--max-depth','4','--reverse']);assert.equal(c.package,'A');assert.equal(c.maxDepth,4);assert.equal(c.reverse,true)});
test('rejects unknown and missing values',()=>{assert.throws(()=>parseArgs(['--oops']));assert.throws(()=>parseArgs(['--package']))});
test('validates package and depth',()=>{assert.ok(validateConfig(parseArgs(['--max-depth','-1'])).length>0)});
