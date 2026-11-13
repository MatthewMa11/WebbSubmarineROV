(() => {
  const button=document.getElementById('whale-ripple');
  const ripple=document.querySelector('.home-ripple');
  const whale=document.querySelector('.whale-depth');
  if(!button||!ripple||!whale)return;
  let timer=0;
  button.addEventListener('click',()=>{
    clearTimeout(timer);ripple.classList.remove('is-pinging');whale.classList.remove('is-called');
    void ripple.offsetWidth;ripple.classList.add('is-pinging');whale.classList.add('is-called');
    document.getElementById('whale-response').textContent='A ripple through our illustrated ocean.';
    timer=setTimeout(()=>{ripple.classList.remove('is-pinging');whale.classList.remove('is-called');document.getElementById('whale-response').textContent='Explore what’s below the surface.';},3100);
  });
})();
