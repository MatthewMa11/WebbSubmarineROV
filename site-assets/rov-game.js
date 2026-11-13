import {newMission,moveRov,scanMission,nearbyFind,recordFind,FIND_SPOTS} from './rov-game-model.mjs';
const $=selector=>document.querySelector(selector);
let mission=newMission();
let lastNear=null;
let thrustTimer=0;
let scanTimer=0;
function renderMission() {
  $('#rov-marker').style.left=mission.x+'%';$('#rov-marker').style.top=mission.y+'%';
  $('#rov-marker').style.setProperty('--heading',mission.heading+'deg');
  $('#mission-coordinates').textContent=`X ${Math.round(mission.x)} / Y ${Math.round(mission.y)}`;
  $('#mission-count').textContent=mission.recorded.length+' / 3 documented';
  $('#mission-scans').textContent=mission.scans+' scans';
  for(const find of FIND_SPOTS) {
    const marker=$(`[data-map-find="${find.id}"]`);
    marker.hidden=!mission.revealed.includes(find.id);marker.classList.toggle('is-recorded',mission.recorded.includes(find.id));
    $(`[data-check-find="${find.id}"]`).classList.toggle('is-recorded',mission.recorded.includes(find.id));
  }
  const near=nearbyFind(mission);
  $('#record-find').disabled=!near;
  $('#map-record').disabled=!near;
  $('#record-find').textContent=near?'Document '+near.name:'Document a find';
  $('#export-mission').disabled=!mission.recorded.length;
  $('#mission-complete').hidden=mission.recorded.length!==3;
  if(near?.id!==lastNear) {
    if(near)$('#mission-status').textContent=near.name+' is within camera range. You can document it.';
    lastNear=near?.id||null;
  }
}
function steer(dx,dy) {
  mission=moveRov(mission,dx,dy);renderMission();
  $('#rov-marker').classList.add('is-thrusting');clearTimeout(thrustTimer);
  thrustTimer=setTimeout(()=>$('#rov-marker').classList.remove('is-thrusting'),200);
}
function scan() {
  const count=mission.revealed.length;mission=scanMission(mission);renderMission();
  const added=mission.revealed.length-count;
  $('#mission-status').textContent=added?`${added} new sonar contact${added===1?'':'s'}. Steer closer to document a find.`:'Scan complete. Move to a new area to find more contacts.';
  const ring=$('#sonar-wave');ring.classList.remove('is-scanning');
  ring.style.left=mission.x+'%';ring.style.top=mission.y+'%';
  void ring.offsetWidth;ring.classList.add('is-scanning');
  clearTimeout(scanTimer);scanTimer=setTimeout(()=>ring.classList.remove('is-scanning'),1600);
}
const directions={up:[0,-5],down:[0,5],left:[-5,0],right:[5,0]};
document.querySelectorAll('[data-steer]').forEach(button=>button.addEventListener('click',()=>steer(...directions[button.dataset.steer])));
document.querySelectorAll('[data-scan]').forEach(button=>button.addEventListener('click',scan));
$('#mission-map').addEventListener('keydown',event=>{
  const key=event.key.toLowerCase();
  const direction={arrowup:'up',w:'up',arrowdown:'down',s:'down',arrowleft:'left',a:'left',arrowright:'right',d:'right'}[key];
  if(direction) {event.preventDefault();steer(...directions[direction]);}
  else if(key===' ') {event.preventDefault();if(!event.repeat)scan();}
});
function documentFind() {
  const find=nearbyFind(mission);if(!find)return;
  mission=recordFind(mission);renderMission();
  $('#mission-status').textContent=mission.recorded.length===3?'Mission complete. All three fictional finds are documented.':find.name+' documented. Keep exploring for the remaining finds.';
}
$('#record-find').addEventListener('click',documentFind);
$('#map-record').addEventListener('click',documentFind);
$('#reset-mission').addEventListener('click',()=>{
  mission=newMission();lastNear=null;renderMission();
  clearTimeout(scanTimer);$('#sonar-wave').classList.remove('is-scanning');
  $('#mission-status').textContent='New mission. Ping sonar, then steer toward a contact.';
});
$('#mission-lights').addEventListener('click',()=>{
  const on=$('#mission-lights').getAttribute('aria-pressed')!=='true';
  $('#mission-lights').setAttribute('aria-pressed',String(on));$('#mission-map').classList.toggle('lights-off',!on);
  $('#mission-lights').textContent=on?'Lights on':'Lights off';
});
$('#export-mission').addEventListener('click',()=>{
  if(!mission.recorded.length)return;
  const log={type:'Fictional ROV training run',scans:mission.scans,documented:FIND_SPOTS.filter(f=>mission.recorded.includes(f.id)).map(f=>({name:f.name,gridX:f.x,gridY:f.y}))};
  const url=URL.createObjectURL(new Blob([JSON.stringify(log,null,2)],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download='rov-training-log.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
renderMission();
