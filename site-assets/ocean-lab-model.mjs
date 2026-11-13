// Educational depth estimates and fictional mission state; no hardware connection.
export function depthInfo(value) {
  const number=Number(value);
  const depth=Math.max(0,Math.min(4000,Number.isFinite(number)?Math.round(number):0));
  const band=depth<200?0:depth<1000?1:depth<4000?2:3;
  return {depth,band,zone:['Sunlight','Twilight','Midnight','Abyss edge'][band],pressure:Math.round(1+depth/10)};
}
export const FIND_SPOTS=Object.freeze([
  Object.freeze({id:'spiral',name:'Spiral shell impression',x:25,y:30}),
  Object.freeze({id:'leaf',name:'Leaf impression',x:75,y:35}),
  Object.freeze({id:'bone',name:'Vertebra fragment',x:65,y:75})
]);
export function newMission() { return {x:50,y:82,heading:0,scans:0,revealed:[],recorded:[]}; }
export function moveRov(state,dx,dy) {
  dx=Number.isFinite(dx)?dx:0;dy=Number.isFinite(dy)?dy:0;
  return {...state,x:Math.max(6,Math.min(94,state.x+dx)),y:Math.max(6,Math.min(94,state.y+dy)),heading:dx||dy?Math.atan2(dx,-dy)*180/Math.PI:state.heading};
}
const distance=(state,find)=>Math.hypot(state.x-find.x,state.y-find.y);
export function scanMission(state) {
  return {...state,scans:state.scans+1,revealed:[...new Set([...state.revealed,...FIND_SPOTS.filter(f=>distance(state,f)<=34).map(f=>f.id)])]};
}
export function nearbyFind(state) {
  return FIND_SPOTS.filter(f=>state.revealed.includes(f.id)&&!state.recorded.includes(f.id)&&distance(state,f)<=10).sort((a,b)=>distance(state,a)-distance(state,b))[0]||null;
}
export function recordFind(state) {
  const find=nearbyFind(state);
  return find?{...state,recorded:[...state.recorded,find.id]}:state;
}
