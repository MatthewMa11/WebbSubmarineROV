// Run from the repository root after npm run build:site.
const {chromium}=require('playwright');
const path=require('node:path');
const assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({headless:true,...(process.env.BROWSER_EXECUTABLE ? {executablePath:process.env.BROWSER_EXECUTABLE} : {})});
try{
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const pages=['index.html','journals/club-mission-and-museum-vision.html','journals/motor-and-fan-cad-development.html'];
 for(const width of [1440,768,390,320]){
  await page.setViewportSize({width,height:900});
  for(const [i,file] of pages.entries()){
   await page.goto('file://'+path.resolve(file));
   await page.locator('img').evaluateAll(async images=>{for(const img of images){img.loading='eager';await img.decode();}});
   await page.waitForTimeout(650);
   const result=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.hash),images:[...document.images].filter(i=>!i.naturalWidth||!i.alt).length}));
   assert(!result.overflow,`${file} overflows at ${width}`);assert.equal(result.broken.length,0);assert.equal(result.images,0);
   if(process.env.SCREENSHOT_DIR && (width===1440||width===390)){await page.screenshot({path:path.resolve(process.env.SCREENSHOT_DIR,'ui-'+i+'-'+width+'.png'),fullPage:true});}
   if(i===1&&width===1440){
    await page.locator('.contents a').nth(2).click();await page.waitForTimeout(1000);
    const box=await page.locator('#bringing-engineering-into-the-museum').boundingBox();
    assert(box.y>=82&&box.y<160,'Deep link should clear sticky header');
    assert.equal(await page.locator('.contents a[aria-current="location"]').count(),1);
    await page.evaluate(()=>scrollTo(0,document.documentElement.scrollHeight));await page.waitForTimeout(1000);
    assert(await page.locator('.reading-progress span').evaluate(e=>getComputedStyle(e).transform==='matrix(1, 0, 0, 1, 0, 0)'));
   }
  }
  console.log(`${width}px: all 3 pages load, images and local anchors valid, no page overflow.`);
 }
 assert.equal(errors.length,0,errors.join('\n'));
 await page.emulateMedia({media:'print'});
 assert.equal(await page.locator('.site-header').evaluate(e=>getComputedStyle(e).position),'static');
 console.log('PASS: journal deep links, reading progress, active section, print layout, no JS errors.');
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
