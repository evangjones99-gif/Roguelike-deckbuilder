/* Review-only, browser-injected prototype. Not shipped/imported by runtime.
 * Manual tick reads the actual navigator.getGamepads API; a production owner
 * would schedule it on an independent RAF with hide/dispose cleanup.
 */
window.ControllerLab={create(){
  let disposed=false,armed=false,lastPad=null,previous=[],lastDirection='',nextRepeat=0,origin=null;
  const visible=e=>!e.disabled&&e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';
  const candidates=root=>[...root.querySelectorAll('button,input,select,textarea')].filter(visible);
  const token=e=>e?.dataset.focus||e?.id||(e?.dataset.ui?`ui:${e.dataset.ui}`:null);
  const find=key=>key?.startsWith('ui:')?document.querySelector(`[data-ui="${CSS.escape(key.slice(3))}"]`):document.getElementById(key)||document.querySelector(`[data-focus="${CSS.escape(key||'')}"]`);
  const focus=e=>{e?.focus({preventScroll:true});e?.scrollIntoView({block:'nearest',inline:'nearest'});};
  function groups(){
    const dialog=document.querySelector('#dialog[open]');
    if(dialog)return [{kind:'dialog',nodes:candidates(dialog)}];
    const targets=[...document.querySelectorAll('.unit.valid-target')].filter(visible);
    if(targets.length)return [{kind:'targets',nodes:targets}];
    if(document.querySelector('#app.phase-battle'))return [
      {kind:'hand',nodes:[...document.querySelectorAll('.hand-cards button')].filter(visible)},
      {kind:'bindings',nodes:[...document.querySelectorAll('.ally')].filter(visible)},
      {kind:'hostiles',nodes:[...document.querySelectorAll('.enemy')].filter(visible)},
      {kind:'turn',nodes:[...document.querySelectorAll('.turn-controls button')].filter(visible)},
      {kind:'tools',nodes:[...document.querySelectorAll('#topbar button,#hud button,.pile-buttons button,[data-ui="log"]')].filter(visible)}
    ].filter(g=>g.nodes.length);
    return [{kind:'menu',nodes:candidates(document.querySelector('#scene-ui'))}];
  }
  function locate(gs){const active=document.activeElement;let group=gs.findIndex(g=>g.nodes.includes(active));if(group<0)group=0;return {group,index:Math.max(0,gs[group]?.nodes.indexOf(active)||0)};}
  function cycleZone(step){const gs=groups();if(!gs.length)return;const {group}=locate(gs);focus(gs[(group+step+gs.length)%gs.length].nodes[0]);}
  function move(direction){
    const active=document.activeElement;
    if(active instanceof HTMLInputElement&&active.type==='range'){
      (['right','up'].includes(direction)?active.stepUp.bind(active):active.stepDown.bind(active))(10);
      active.dispatchEvent(new Event('input',{bubbles:true}));return;
    }
    if(active instanceof HTMLSelectElement){active.selectedIndex=Math.max(0,Math.min(active.options.length-1,active.selectedIndex+(['right','down'].includes(direction)?1:-1)));active.dispatchEvent(new Event('input',{bubbles:true}));active.dispatchEvent(new Event('change',{bubbles:true}));return;}
    const gs=groups();if(!gs.length)return;const {group,index}=locate(gs),current=gs[group];
    if(['bindings','hostiles'].includes(current.kind)&&['left','right'].includes(direction)){
      const destination=gs.find(g=>g.kind===(direction==='right'?'hostiles':'bindings'))||gs.find(g=>g.kind==='hand');focus(destination?.nodes[Math.min(index,(destination?.nodes.length||1)-1)]);return;
    }
    if(current.kind==='hand'&&direction==='up'){focus((gs.find(g=>g.kind==='bindings')||gs.find(g=>g.kind==='hostiles'))?.nodes[0]);return;}
    if(['dialog','menu'].includes(current.kind)) {
      const rect=current.nodes[index].getBoundingClientRect(),cx=rect.x+rect.width/2,cy=rect.y+rect.height/2;
      const dx=direction==='right'?1:direction==='left'?-1:0,dy=direction==='down'?1:direction==='up'?-1:0;
      const ranked=current.nodes.filter(e=>e!==current.nodes[index]).map(node=>{const r=node.getBoundingClientRect(),x=r.x+r.width/2-cx,y=r.y+r.height/2-cy;return {node,forward:x*dx+y*dy,cross:Math.abs(x*dy-y*dx)};}).filter(x=>x.forward>1).sort((a,b)=>(a.forward+a.cross*2)-(b.forward+b.cross*2));
      if(ranked.length){focus(ranked[0].node);return;}
    }
    const step=['right','down'].includes(direction)?1:-1;
    focus(current.nodes[(index+step+current.nodes.length)%current.nodes.length]);
  }
  function recoverFocus(){if(document.activeElement!==document.body)return;const heading=document.querySelector('#scene-ui .page-intro h1');if(!document.querySelector('#app.phase-battle')&&heading){heading.tabIndex=-1;focus(heading);return;}focus(document.querySelector('.ally.ready')||document.querySelector('.hand-cards button')||groups()[0]?.nodes[0]);}
  function activate(){
    const gs=groups(),active=document.activeElement;
    if(!gs.some(g=>g.nodes.includes(active))) {focus(gs[0]?.nodes[0]);return;}
    if(active instanceof HTMLButtonElement){
      const source=token(active),wasTargeting=!!document.querySelector('.unit.valid-target');active.click();
      if(!wasTargeting&&document.querySelector('.unit.valid-target'))origin=source;
      recoverFocus();
    }else if(active instanceof HTMLInputElement&&['checkbox','radio'].includes(active.type))active.click();
  }
  function back(){const dialog=document.querySelector('#dialog[open]');if(dialog){dialog.close();recoverFocus();return;}const cancel=document.querySelector('[data-ui="cancel"]');if(cancel){cancel.click();focus(find(origin));origin=null;return;}document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));}
  function inspect(){const active=document.activeElement;if(active.dataset.unit)document.querySelector(`[data-ui="inspect-unit"][data-uid="${CSS.escape(active.dataset.unit)}"]`)?.click();}
  function reset(){armed=false;previous=[];lastDirection='';nextRepeat=0;}
  function tick(now){
    if(disposed)return;
    let pads;try{pads=navigator.getGamepads?.();}catch{reset();return;}
    const pad=[...(pads||[])].find(p=>p?.connected&&p.mapping==='standard');
    if(!pad||document.hidden){lastPad=null;reset();return;}
    if(lastPad!==pad.index){lastPad=pad.index;reset();}
    const held=Array.from({length:17},(_,i)=>!!pad.buttons[i]?.pressed||Number(pad.buttons[i]?.value)>=.6);
    const x=Number.isFinite(pad.axes[0])?pad.axes[0]:0,y=Number.isFinite(pad.axes[1])?pad.axes[1]:0;
    if(!armed){previous=held;if(!held.some(Boolean)&&Math.abs(x)<.3&&Math.abs(y)<.3)armed=true;return;}
    const edge=i=>held[i]&&!previous[i];
    const blocked=document.querySelector('#app.settling-combat')&&!document.querySelector('#dialog[open]');
    if(edge(9)&&!document.querySelector('#dialog[open]'))document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
    if(!blocked){
      if(edge(1))back();else if(edge(0))activate();else if(edge(2))inspect();
      if(edge(3)&&!document.querySelector('#dialog[open]'))document.querySelector('[data-action="endTurn"]:not(:disabled)')?.click();
      if(edge(4))cycleZone(-1);if(edge(5))cycleZone(1);
      let direction=held[12]?'up':held[13]?'down':held[14]?'left':held[15]?'right':'';
      const threshold=.55;
      if(!direction&&Math.max(Math.abs(x),Math.abs(y))>threshold)direction=Math.abs(x)>Math.abs(y)?x>0?'right':'left':y>0?'down':'up';
      if(!direction&&Math.max(Math.abs(x),Math.abs(y))>.3)direction=lastDirection;
      if(direction&&(direction!==lastDirection||now>=nextRepeat)){move(direction);nextRepeat=now+(direction!==lastDirection?350:100);}
      if(!direction)nextRepeat=0;lastDirection=direction;
    }else{lastDirection='';nextRepeat=0;}
    previous=held;
  }
  return {tick,dispose(){disposed=true;reset();}};
}};
