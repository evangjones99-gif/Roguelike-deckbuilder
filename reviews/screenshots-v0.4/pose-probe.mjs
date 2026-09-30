import fs from 'node:fs/promises';
/** Capture completed canvas frames when a distinct atlas cell becomes dominant.
 * This records rendered images and source-cell selection, not skeletal motion.
 * Do not use PNG-probed windows for the independent cadence measurement. */
export async function installPoseProbe(context, suffix='hound-poses.png') {
  await context.addInitScript(assetSuffix=>{
    window.visualPoseRecords=[];window.visualPoseImages=[];window.visualPoseSeen={};
    const draw=CanvasRenderingContext2D.prototype.drawImage;
    CanvasRenderingContext2D.prototype.drawImage=function(...args){
      const result=draw.apply(this,args),asset=args[0];
      if(this.canvas.id==='arena'&&asset instanceof HTMLImageElement&&asset.src.endsWith(assetSuffix)&&args.length===9){
        const record={time:performance.now(),url:asset.src,naturalWidth:asset.naturalWidth,naturalHeight:asset.naturalHeight,sx:args[1],sy:args[2],sw:args[3],sh:args[4],dx:args[5],dy:args[6],dw:args[7],dh:args[8],alpha:this.globalAlpha};
        window.visualPoseRecords.push(record);
        const key=[record.sx,record.sy,record.sw,record.sh].join('-');
        if(record.alpha>=.92&&!window.visualPoseSeen[key]){
          window.visualPoseSeen[key]=true;
          const canvas=this.canvas;
          queueMicrotask(()=>window.visualPoseImages.push({...record,key,data:canvas.toDataURL('image/png')}));
        }
      }
      return result;
    };
  },suffix);
}
export async function drainPoseProbe(page,directory){
  const result=await page.evaluate(()=>({records:window.visualPoseRecords||[],images:window.visualPoseImages||[]}));
  const frames=[];
  for(let i=0;i<result.images.length;i++){
    const{data,...metadata}=result.images[i],file=`${directory}/pose-rendered-${i}.png`;
    await fs.writeFile(file,Buffer.from(data.split(',')[1],'base64'));frames.push({...metadata,file});
  }
  await fs.writeFile(`${directory}/pose-draw-records.json`,JSON.stringify({records:result.records,frames},null,2));
  return{draws:result.records.length,frames};
}
