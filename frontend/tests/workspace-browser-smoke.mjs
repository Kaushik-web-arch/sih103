// Option B interactions, responsive layout and reference-data boundaries.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdir } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { once } from 'node:events';
import { chromium as playwright } from 'playwright-core';
import chromium from '@sparticuz/chromium';
const root=resolve(import.meta.dirname,'../dist');
const server=createServer(async(req,res)=>{
  const path=resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(path!==root && !path.startsWith(root+sep)){res.writeHead(403).end();return;}
  try {
    const file=path===root?resolve(root,'index.html'):path;
    const bytes=await readFile(file);
    res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json'})[extname(file)]||'application/octet-stream');res.end(bytes);
  } catch {res.writeHead(404).end();}
});
let browser;
try {
 server.listen(0,'127.0.0.1');await once(server,'listening');
 browser=await playwright.launch({args:chromium.args,executablePath:await chromium.executablePath(),headless:true});
 const p=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(`http://127.0.0.1:${server.address().port}/`,{waitUntil:'networkidle'});
 await p.getByRole('heading',{name:'Find a project'}).waitFor();
 await p.locator('.project-name').first().waitFor();
 const capture=async name=>{if(process.env.SENTINEL_SCREENSHOTS){await mkdir(process.env.SENTINEL_SCREENSHOTS,{recursive:true});await p.screenshot({path:resolve(process.env.SENTINEL_SCREENSHOTS,name+'.png'),fullPage:true});}};
 await capture('desktop');
 await p.locator('.project-name').first().click();
 await p.locator('.detail-pane .value-card').first().waitFor();
 assert.equal(await p.locator('.detail-pane [aria-modal="true"]').count(),0);
 assert.equal(await p.evaluate(()=>document.body.style.overflow),'');
 const list=await p.locator('.project-results').boundingBox(),detail=await p.locator('.detail-pane').boundingBox();
 assert.ok(detail.x>list.x+list.width,'Desktop details must sit beside the results');
 await capture('selected');
 await p.getByRole('tab',{name:'History',exact:true}).click();
 await p.locator('.drawer-body').getByText('Loading',{exact:false}).waitFor({state:'hidden'});
 await p.getByRole('tab',{name:'Source',exact:true}).click();
 await capture('source');
 await p.getByRole('button',{name:'Close inspector'}).click();
 await p.getByLabel('Search project names').fill('zzzz-no-matching-project');
 await p.getByRole('heading',{name:'No matching projects'}).waitFor();
 await p.getByRole('button',{name:'Reset search'}).click();
 await p.locator('.project-name').first().waitFor();
 await p.getByRole('button',{name:'Switch to dark mode'}).click();
 assert.equal(await p.locator('html').getAttribute('data-theme'),'dark');
 await capture('dark');
 await p.getByRole('button',{name:'Switch to light mode'}).click();
 await p.setViewportSize({width:390,height:844});
 await p.locator('.project-name').first().click();
 await p.locator('.detail-pane .value-card').first().waitFor();
 assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile layout overflows viewport');
 await capture('mobile');
 await p.getByRole('button',{name:'Close inspector'}).click();
 for(const name of ['Portfolio','Sources & gaps','Report changes','Projects']){
   await p.getByRole('navigation').getByRole('button',{name,exact:true}).click();
   await capture(name.replaceAll(' ','-'));
   const over = await p.evaluate(()=>[...document.querySelectorAll('main *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).slice(0,8).map(e=>({tag:e.tagName,cls:e.className,width:e.getBoundingClientRect().width})));
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${name} mobile overflow ${JSON.stringify(over)}`);
 }
 assert.deepEqual(errors,[]);
 console.log('PASS: Option B workspace — selection, history/source, search reset, theme, mobile and navigation');
} finally {await browser?.close(); await new Promise(r=>server.close(r));}
