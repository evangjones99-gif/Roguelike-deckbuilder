/** Lower jaw retains the original painted texture and rigid proportions. */
const contour = [[378,278],[389,280],[398,287],[408,295],[417,300],[425,306],
  [421,324],[412,337],[397,335],[392,318],[386,302],[375,289]] as const;
const hinge = {x:379,y:278};
const smooth = (v: number) => { const t=Math.max(0,Math.min(1,v));return t*t*(3-2*t); };
export function houndJawClosure(age: number): number {
  if(age<.18||age>=.36)return 0;
  return age<.24?smooth((age-.18)/.06):age<.28?1:1-smooth((age-.28)/.08);
}
export function houndJawPoint(x:number,y:number,closure:number) {
  const angle=-.62*closure,c=Math.cos(angle),s=Math.sin(angle),dx=x-hinge.x,dy=y-hinge.y;
  return {x:hinge.x+dx*c-dy*s,y:hinge.y+dx*s+dy*c};
}
let surface:HTMLCanvasElement|undefined;
let sourceImage:HTMLImageElement|undefined;
let sourceCellX=-1,sourceCellY=-1;
let anatomyPath:Path2D|undefined;
function sourceJawPath(){
  if(!anatomyPath){anatomyPath=new Path2D();anatomyPath.moveTo(contour[0][0],contour[0][1]);for(const point of contour.slice(1))anatomyPath.lineTo(point[0],point[1]);anatomyPath.closePath();}
  return anatomyPath;
}
export function drawHoundJaw(ctx:CanvasRenderingContext2D,image:HTMLImageElement,closure:number,
  sourceX:number,sourceY:number,cropX:number,cropY:number,cropWidth:number,cropHeight:number,
  destinationX:number,destinationY:number,destinationWidth:number,destinationHeight:number) {
  // Fully opaque actors need no intermediate texture/compositing round trip.
  // Partial appearance fades retain the single-opacity texture path below.
  if(ctx.globalAlpha===1){
    ctx.save();ctx.translate(destinationX,destinationY);
    ctx.scale(destinationWidth/cropWidth,destinationHeight/cropHeight);ctx.translate(-cropX,-cropY);
    const jaw=sourceJawPath(),base=new Path2D();base.rect(cropX,cropY,cropWidth,cropHeight);base.addPath(jaw);
    ctx.save();ctx.clip(base,'evenodd');ctx.drawImage(image,sourceX,sourceY,512,512,0,0,512,512);ctx.restore();
    ctx.save();ctx.translate(hinge.x,hinge.y);ctx.rotate(-.62*closure);ctx.translate(-hinge.x,-hinge.y);
    ctx.clip(jaw);ctx.drawImage(image,sourceX,sourceY,512,512,0,0,512,512);ctx.restore();ctx.restore();
    return;
  }
  const texture=surface??=document.createElement('canvas');
  if(texture.width!==512){texture.width=512;texture.height=512;}
  const ink=texture.getContext('2d');
  if(!ink){ctx.drawImage(image,sourceX+cropX,sourceY+cropY,cropWidth,cropHeight,destinationX,destinationY,destinationWidth,destinationHeight);return;}
  const jawPath=()=>{ink.beginPath();ink.moveTo(contour[0][0],contour[0][1]);for(const point of contour.slice(1))ink.lineTo(point[0],point[1]);ink.closePath();};
  if(sourceImage!==image||sourceCellX!==sourceX||sourceCellY!==sourceY){
    ink.clearRect(0,0,512,512);
    ink.drawImage(image,sourceX,sourceY,512,512,0,0,512,512);
    sourceImage=image;sourceCellX=sourceX;sourceCellY=sourceY;
  }
  // Reset only the conservative jaw envelope; all other source pixels stay cached.
  ink.clearRect(373,272,80,68);
  ink.drawImage(image,sourceX+373,sourceY+272,80,68,373,272,80,68);
  // Remove the old jaw so it cannot remain doubled under the closing layer.
  ink.save();ink.globalCompositeOperation='destination-out';jawPath();ink.fill();ink.restore();
  ink.save();ink.translate(hinge.x,hinge.y);ink.rotate(-.62*closure);ink.translate(-hinge.x,-hinge.y);
  jawPath();ink.clip();ink.drawImage(image,sourceX,sourceY,512,512,0,0,512,512);ink.restore();
  // Apply figure opacity once after assembling both anatomy layers.
  ctx.drawImage(texture,cropX,cropY,cropWidth,cropHeight,destinationX,destinationY,destinationWidth,destinationHeight);
}
