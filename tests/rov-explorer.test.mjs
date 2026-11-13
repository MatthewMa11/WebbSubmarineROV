import test from 'node:test';
import assert from 'node:assert/strict';
import { depthInfo, newMission, moveRov, scanMission, nearbyFind, recordFind } from '../site-assets/rov-explorer-model.mjs';

test('depth explorer uses the correct zone at each light boundary', () => {
  for (const [input,zone] of [[0,'Sunlight'],[199,'Sunlight'],[200,'Twilight'],[999,'Twilight'],[1000,'Midnight'],[3999,'Midnight'],[4000,'Abyss edge']]) {
    assert.equal(depthInfo(input).zone,zone);
  }
});
test('depth and pressure remain bounded for invalid and out-of-range slider values', () => {
  assert.equal(depthInfo(-10).depth,0);
  assert.equal(depthInfo('bad').depth,0);
  assert.equal(depthInfo(9000).depth,4000);
  assert.equal(depthInfo(0).pressure,1);
  assert.equal(depthInfo(1000).pressure,101);
  assert.equal(depthInfo(4000).pressure,401);
});
test('steering cannot leave the training map or corrupt the position', () => {
  const start=newMission();
  assert.deepEqual([start.x,start.y],[50,82]);
  const moved=moveRov(start,-100,100);
  assert.deepEqual([moved.x,moved.y],[6,94]);
  assert.deepEqual([start.x,start.y],[50,82]);
  assert.deepEqual([moveRov(start,NaN,0).x,moveRov(start,NaN,0).y],[50,82]);
});
test('a scan reveals only targets in sonar range', () => {
  const state=scanMission(newMission());
  assert.deepEqual(state.revealed,['bone']);
  assert.equal(state.scans,1);
  assert.equal(nearbyFind(state),null);
});
test('a find must be scanned and approached before it can be documented', () => {
  const close={...newMission(),x:65,y:75};
  assert.equal(nearbyFind(close),null);
  assert.equal(recordFind(close).recorded.length,0);
  const scanned=scanMission(close);
  assert.equal(nearbyFind(scanned).id,'bone');
  const recorded=recordFind(scanned);
  assert.deepEqual(recorded.recorded,['bone']);
  assert.deepEqual(scanned.recorded,[]);
  assert.equal(nearbyFind(recorded),null);
  assert.equal(recordFind(recorded).recorded.length,1);
});
test('the mission can complete all three finds and reset cleanly', () => {
  let state=newMission();
  for(const [x,y] of [[25,30],[75,35],[65,75]]) state=recordFind(scanMission({...state,x,y}));
  assert.deepEqual(state.recorded,['spiral','leaf','bone']);
  const reset=newMission();
  assert.deepEqual(reset.recorded,[]);
  assert.deepEqual(reset.revealed,[]);
  assert.equal(reset.scans,0);
});
