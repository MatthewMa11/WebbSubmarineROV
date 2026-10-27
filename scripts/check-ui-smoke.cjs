// Run from the repository root after npm run build:site.
const { chromium }=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
(async()=>{
const browser=await chromium.launch({headless:true,...(process.env.BROWSER_EXECUTABLE ? {executablePath:process.env.BROWSER_EXECUTABLE} : {})});
try {
 const page=await browser.newPage({viewport:{width:390,height:844}});
 await page.goto('file://'+path.resolve('index.html'));
 const menu=page.getByRole('button',{name:'Menu',exact:true});
 assert.equal(await menu.count(),1,'Phone visitors need a navigation menu button');
 await menu.click();
 assert.equal(await menu.getAttribute('aria-expanded'),'true');
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Journals',exact:true}).focus();
 await page.keyboard.press('Escape');
 assert.equal(await menu.getAttribute('aria-expanded'),'false');
 assert.equal(await menu.evaluate(e=>e===document.activeElement),true,'Escape returns focus');
 await menu.click();
 await page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Journals',exact:true}).click();
 assert.equal(await menu.getAttribute('aria-expanded'),'false');
 assert.equal(await page.evaluate(()=>document.activeElement.id),'journal','Selected section receives focus');
 const animated=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'no-preference'});
 await animated.goto('file://'+path.resolve('index.html'));
 await animated.evaluate(()=>window.scrollTo({top:document.getElementById('downloads').offsetTop,behavior:'instant'}));
 await animated.waitForFunction(()=>document.querySelector('.download-row').getAnimations().some(a=>a.playState==='running'));
 await animated.emulateMedia({reducedMotion:'reduce'});
 await animated.waitForFunction(()=>document.getAnimations().every(a=>a.playState!=='running'));
 const reduced=await browser.newPage({reducedMotion:'reduce'});
 await reduced.goto('file://'+path.resolve('index.html'));
 assert.equal(await reduced.evaluate(()=>getComputedStyle(document.documentElement).scrollBehavior),'auto');
 await reduced.locator('#journal').scrollIntoViewIfNeeded();
 assert.equal(await reduced.evaluate(()=>document.getAnimations().filter(a=>a.playState==='running').length),0);
 const plain=await browser.newPage({javaScriptEnabled:false,viewport:{width:390,height:844}});
 await plain.goto('file://'+path.resolve('index.html'));
 assert(await plain.getByRole('navigation',{name:'Main navigation'}).isVisible());
 assert(await plain.locator('#journal').isVisible());
 console.log('PASS: mobile menu, Escape/focus, anchor navigation, scroll animation, live reduced-motion changes and no-JS navigation.');
}finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
