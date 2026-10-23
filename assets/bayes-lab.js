(() => {
  const root = document.getElementById('bayes-lab');
  if (!root) return;
  const eta = root.querySelector('#eta'), samples = root.querySelector('#samples'), seed = root.querySelector('#seed');
  const canvas = root.querySelector('canvas'), ctx = canvas.getContext('2d');
  function draw() {
    const strength=Number(eta.value), count=Number(samples.value);
    let state=(Number(seed.value)||1)>>>0;
    const rand=()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return state/4294967296;};
    const hidden=rand()<.5?1:-1;
    const probs=[.5], entropies=[1]; let odds=0;
    for(let t=0;t<count;t++){
      const m=rand()<(1+strength*hidden)/2?1:-1;
      if(strength===1) odds=hidden*1000;
      else odds+=m*Math.log((1+strength)/(1-strength));
      const q=odds>=0?1/(1+Math.exp(-odds)):Math.exp(odds)/(1+Math.exp(odds));
      probs.push(q);
      const h=-(q>0?q*Math.log(q):0)-(q<1?(1-q)*Math.log(1-q):0);
      entropies.push(h/Math.log(2));
    }
    root.querySelector('#eta-out').textContent=strength.toFixed(2);
    root.querySelector('#samples-out').textContent=count;
    root.querySelector('#bayes-status').textContent=`True hidden value: ${hidden>0?'+1':'−1'}. Final P(z=+1): ${probs.at(-1).toFixed(4)}. Teal: posterior; coral: entropy / ln 2.`;
    const W=canvas.width,H=canvas.height, l=60,r=20,top=20,b=50;
    ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);
    ctx.font='15px sans-serif';ctx.lineWidth=1;
    for(let v=0;v<=1.001;v+=.25){const y=top+(1-v)*(H-top-b);ctx.strokeStyle='#e0e7eb';ctx.beginPath();ctx.moveTo(l,y);ctx.lineTo(W-r,y);ctx.stroke();ctx.fillStyle='#35465a';ctx.fillText(v.toFixed(2),10,y+5);}
    ctx.fillStyle='#35465a';ctx.fillText('Readout number',W/2-50,H-10);ctx.fillText('0',l-3,H-25);ctx.fillText(String(count),W-r-25,H-25);
    for(const [arr,color] of [[probs,'#167d8d'],[entropies,'#c45d3e']]){ctx.strokeStyle=color;ctx.lineWidth=2.5;ctx.beginPath();arr.forEach((v,i)=>{const x=l+i/count*(W-l-r),y=top+(1-v)*(H-top-b);i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();}
  }
  [eta,samples,seed].forEach(el=>el.addEventListener('input',draw));
  root.querySelector('#resample').addEventListener('click',()=>{seed.value=(Number(seed.value)||1)+1;draw();});
  draw();
})();
