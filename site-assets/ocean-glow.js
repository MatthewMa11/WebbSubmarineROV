// A bounded light-painting canvas inspired by bioluminescence.
(() => {
  const canvas=document.getElementById('glow-canvas');
  const context=canvas?.getContext('2d',{alpha:false});
  if(!context)return;
  const root=document.documentElement;
  const count=document.getElementById('glow-count');
  const palettes={lagoon:[88,255,223],abyss:[112,173,255],violet:[224,133,255]};
  let palette='lagoon',current=20,width=0,height=0,frame=0,last=0,visible=false,painting=false,lastPaint=0,blooms=0;
  let particles=[];
  const canRun=()=>visible&&particles.length>0&&!root.classList.contains('motion-paused')&&document.visibilityState!=='hidden';
  function draw() {
    context.fillStyle='#040d1c';context.fillRect(0,0,width,height);
    for(let i=0;i<24;i++) {
      context.fillStyle=i%3===0?'#153a4a':'#10283e';context.beginPath();context.arc(((i*137.9)%1)*width,((i*93.71)%1)*height,1.2,0,Math.PI*2);context.fill();
    }
    context.globalCompositeOperation='lighter';
    for(const p of particles) {
      const alpha=Math.max(0,p.life/p.total);
      const radius=p.radius*(1+(1-alpha)*2);
      const color=p.color.join(',');
      const glow=context.createRadialGradient(p.x,p.y,0,p.x,p.y,radius);
      glow.addColorStop(0,`rgba(${color},${alpha*.8})`);glow.addColorStop(.22,`rgba(${color},${alpha*.3})`);glow.addColorStop(1,`rgba(${color},0)`);
      context.fillStyle=glow;context.beginPath();context.arc(p.x,p.y,radius,0,Math.PI*2);context.fill();
    }
    context.globalCompositeOperation='source-over';
  }
  function loop(now) {
    frame=0;if(!canRun())return;
    if(!last)last=now;
    const elapsed=now-last;
    if(elapsed>=1000/30) {
      const dt=Math.min(elapsed,80)/1000;last=now;
      particles=particles.filter(p=>p.life>0);
      for(const p of particles) {p.x+=(p.vx+current*.25)*dt;p.y+=p.vy*dt;p.life-=dt;}
      draw();
    }
    frame=requestAnimationFrame(loop);
  }
  function sync() {
    if(canRun()) {if(!frame){last=0;frame=requestAnimationFrame(loop);}}
    else {if(frame)cancelAnimationFrame(frame);frame=0;last=0;draw();}
  }
  function bloom(x=width*.5,y=height*.5,announce=true) {
    for(let i=0;i<10;i++) {
      const angle=Math.random()*Math.PI*2,speed=6+Math.random()*18,total=5+Math.random()*4;
      particles.push({x,y,vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed-3,radius:8+Math.random()*11,life:total,total,color:palettes[palette]});
    }
    const limit=width<760?130:220;
    if(particles.length>limit)particles.splice(0,particles.length-limit);
    blooms++;count.textContent=blooms+' light blooms';
    if(announce)document.getElementById('glow-announcement').textContent='A '+palette+' light bloom was created.';
    draw();sync();
  }
  function resize() {
    const rect=canvas.getBoundingClientRect(),ratio=Math.min(devicePixelRatio||1,1.5);
    if(width&&height)for(const p of particles){p.x*=rect.width/width;p.y*=rect.height/height;}
    width=rect.width;height=rect.height;
    canvas.width=Math.round(width*ratio);canvas.height=Math.round(height*ratio);context.setTransform(ratio,0,0,ratio,0,0);draw();
  }
  function paint(event) {
    const rect=canvas.getBoundingClientRect();bloom(event.clientX-rect.left,event.clientY-rect.top,false);
  }
  canvas.addEventListener('pointerdown',event=>{painting=true;lastPaint=performance.now();canvas.setPointerCapture(event.pointerId);paint(event);});
  canvas.addEventListener('pointermove',event=>{if(painting&&performance.now()-lastPaint>35){lastPaint=performance.now();paint(event);}});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>{painting=false;});
  document.getElementById('create-glow').addEventListener('click',()=>bloom(width*(.25+Math.random()*.5),height*(.25+Math.random()*.5)));
  document.getElementById('clear-glow').addEventListener('click',()=>{particles=[];blooms=0;count.textContent='0 light blooms';draw();document.getElementById('glow-announcement').textContent='The water is clear. Create another glow.';});
  document.getElementById('glow-current').addEventListener('input',event=>{current=Number(event.target.value);document.getElementById('current-value').textContent=current===0?'Still':current>0?'Right '+current:'Left '+Math.abs(current);});
  document.querySelectorAll('[data-palette]').forEach(button=>button.addEventListener('click',()=>{
    palette=button.dataset.palette;document.querySelectorAll('[data-palette]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    document.getElementById('glow-announcement').textContent=palette+' selected for the next light bloom.';
  }));
  new ResizeObserver(resize).observe(canvas);
  new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();}).observe(canvas);
  window.addEventListener('rov-motion-change',sync);document.addEventListener('visibilitychange',sync);
  window.addEventListener('beforeprint',()=>{if(frame)cancelAnimationFrame(frame);frame=0;});
  window.addEventListener('afterprint',sync);resize();
})();
