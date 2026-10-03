import { chromium } from '/workspace/Roguelike-deckbuilder/node_modules/playwright/index.mjs';
import fs from 'node:fs';import crypto from 'node:crypto';
const folder='/workspace/scratch/v06-short-height';
const css=`@media(min-width:1600px) and (max-height:800px){
.phase-battle #topbar{height:58px}
.phase-battle #hud{height:64px}
.phase-battle #dock{height:255px;padding-top:9px;padding-bottom:13px}
.phase-battle .battle-ui{grid-template-rows:38px minmax(0,1fr)}
.phase-battle #arena-wrap{top:39px}
.phase-battle .hand-heading{margin-bottom:7px}
.phase-battle .hand-cards{height:209px}
.phase-battle .hand-cards .game-card{height:201px}
.phase-battle .hand-cards .card-art{height:46px}
.phase-battle .hand-cards .card-description{line-height:1.25}
}`;
fs.writeFileSync(folder+'/candidate.css',css+'\n');
const fixture=JSON.parse(fs.readFileSync('/workspace/Roguelike-deckbuilder/reviews/screenshots-v0.2/full-fixture.json'));
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const outcomes=[];
for(const size of [{width:1920,height:720},{width:1920,height:800},{width:1920,height:900},{width:1600,height:720},{width:2560,height:720}]){
 const page=await browser.newPage({viewport:size});
 await page.addInitScript(s=>{localStorage.setItem('hollowpact.run.v2',JSON.stringify(s));localStorage.setItem('hollowpact.settings.v2',JSON.stringify({motion:false,mute:true,volume:0}));},fixture);
 await page.goto('http://127.0.0.1:4173');await page.locator('[data-ui=resume]').click();
 const raw=await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'));
 const measure=()=>page.evaluate(()=>{
  const rosters=[...document.querySelectorAll('.roster')].map(roster=>{
   const r=roster.getBoundingClientRect();
   return {height:r.height,scroll:roster.scrollHeight,client:roster.clientHeight,units:[...roster.querySelectorAll('.unit')].map(unit=>{const u=unit.getBoundingClientRect();const i=unit.querySelector('.unit-status').getBoundingClientRect();return {top:u.top,bottom:u.bottom,intentFont:getComputedStyle(unit.querySelector('.unit-status')).fontSize,contained:u.top>=r.top-1&&u.bottom<=r.bottom+1&&i.bottom<=u.bottom+1}})};
  });
  const cards=[...document.querySelectorAll('.hand-cards .game-card')].map(card=>{const c=card.getBoundingClientRect();return {id:card.dataset.card,height:c.height,checks:[...card.querySelectorAll('.card-name,.card-description,.card-stats')].map(part=>{const r=part.getBoundingClientRect();return {class:part.className,font:getComputedStyle(part).fontSize,contained:r.top>=c.top-1&&r.bottom<=c.bottom+1&&r.left>=c.left-1&&r.right<=c.right+1}})}});
  return {rosters,cards};
 });
 const baseline=await measure();await page.screenshot({path:`${folder}/baseline-${size.width}-${size.height}.png`});
 await page.addStyleTag({content:css});const candidate=await measure();await page.screenshot({path:`${folder}/candidate-${size.width}-${size.height}.png`});
 outcomes.push({size,baseline,candidate,saveUnchanged:raw===await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'))});
 await page.close();
}
await browser.close();fs.writeFileSync(folder+'/results.json',JSON.stringify({build:'d33ce538e38d98eba6ec06f90660252d53d3f3fc0122c7316b229f043489b52c',method:'Isolated CSS injection; no source edits or production acceptance yet',cssSHA256:crypto.createHash('sha256').update(css+'\n').digest('hex'),outcomes},null,2)+'\n');
console.log(JSON.stringify(outcomes.map(x=>({size:x.size,all12Fit:x.candidate.rosters.every(r=>r.units.every(u=>u.contained)),cardsFit:x.candidate.cards.every(c=>c.checks.every(p=>p.contained)),saveUnchanged:x.saveUnchanged}))));
