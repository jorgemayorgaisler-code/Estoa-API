import test from "node:test";
import assert from "node:assert/strict";
import {createPrivateApi} from "../src/privateApi.js";
test("private transport rejects insecure origin",()=>assert.throws(()=>createPrivateApi("http://example.com","token")));
test("private transport does not fall back on denial",async()=>{
 const original=globalThis.fetch;
 let calls=0;
 globalThis.fetch=async(url,options)=>{calls++;assert.equal(url.pathname,"/private/conditions/now");assert.equal(options.headers.Authorization,"Bearer token");return {status:403,ok:false}};
 try{await assert.rejects(createPrivateApi("https://example.com","token")("/conditions/now"),/no incluida/);assert.equal(calls,1)}finally{globalThis.fetch=original}
});
