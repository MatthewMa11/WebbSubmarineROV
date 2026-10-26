const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('C:/Users/ROG/.codex/visualizations/2026/10/11/01a1298c-fcac-7933-9da5-ab6e5791b2d1/r7-collar-assembly.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
assert(!html.includes('\\"')&&!html.includes('\\n'));
assert(Buffer.byteLength(html)<1e6);
for(const width of [320,736])for(const reduced of [true,false]) {
 class E {
  constructor(){this.attrs={};this.children=[];this.handlers={};this.textContent='';}
  setAttribute(k,v){this.attrs[k]=v;}
  appendChild(n){this.children.push(n);return n;}
  replaceChildren(){this.children=[];}
  addEventListener(n,f){this.handlers[n]=f;}
 }
 const svg=new E(),label=new E(),buttons=Array.from({length:6},(_,i)=>Object.assign(new E(),{dataset:{step:String(i)}}));
 const root={querySelector:s=>s==='.r7-section'?svg:s==='[data-stage-label]'?label:null,querySelectorAll:s=>s==='[data-step]'?buttons:[],getBoundingClientRect:()=>({width})};
 const events={},frames=new Map(),saved=[];let frameId=0,now=0;
 const context={document:{getElementById:id=>id==='r7-assembly-explainer'?root:null,createElementNS:()=>new E()},window:{matchMedia:()=>({matches:reduced}),addEventListener:(k,f)=>events[k]=f,openai:{widgetState:{},setWidgetState:s=>{saved.push(s);return Promise.resolve();}}},ResizeObserver:class{observe(){}},performance:{now:()=>now},requestAnimationFrame:f=>{frames.set(++frameId,f);return frameId;},cancelAnimationFrame:id=>frames.delete(id)};
 vm.runInNewContext(script,context);
 const render=()=>{
  while(frames.size){const entries=[...frames];frames.clear();now+=1000;for(const [,fn]of entries)fn(now);}
  assert(svg.children.length>20);
  for(const el of svg.children)for(const value of Object.values(el.attrs))assert(!/NaN|undefined|Infinity/.test(String(value)),JSON.stringify(el.attrs));
 };
 render();const first=JSON.stringify(svg.children.map(q=>q.attrs));
 for(let n=1;n<6;n++) {
  buttons[n].handlers.click();render();
  assert.strictEqual(buttons[n].attrs['aria-pressed'],'true');
  assert(saved.at(-1).privateContent.r7AssemblyStep===n);
  assert(label.textContent.length>0);
 }
 assert.notStrictEqual(first,JSON.stringify(svg.children.map(q=>q.attrs)));
 events['openai:set_globals']({detail:{globals:{widgetState:{privateContent:{r7AssemblyStep:2}}}}});render();
 assert.strictEqual(buttons[2].attrs['aria-pressed'],'true');
 console.log(`PASS ${width}px, reduced motion ${reduced}: all stages, animation, SVG coordinates and saved state`);
}
