"""Original textbook figures. Requires NumPy and Matplotlib; no downloaded art."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'figs'; OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelsize':11,'figure.dpi':140,'savefig.dpi':220})
teal='#167d8d'; coral='#c45d3e'; navy='#253955'; gold='#bb8e32'
def save(fig,name):
    fig.savefig(OUT/(name+'.png'),bbox_inches='tight',facecolor='white')
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',facecolor='white')
    plt.close(fig)

def box(ax,xy,w,h,text,color=teal):
    ax.add_patch(FancyBboxPatch(xy,w,h,boxstyle='round,pad=0.06',fc=color,ec='none',alpha=.12))
    ax.text(xy[0]+w/2,xy[1]+h/2,text,ha='center',va='center',color=navy)
def arrow(ax,a,b,label=None):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':navy,'lw':1.5})
    if label: ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.12,label,ha='center',fontsize=10)
fig,ax=plt.subplots(figsize=(9,4.2)); ax.set(xlim=(0,10),ylim=(0,4)); ax.axis('off')
box(ax,(.2,1.5),2,1,'System + apparatus\nunitary coupling')
box(ax,(3.2,1.5),2.2,1,'Classical record $m$\nBorn probability $p_m$')
box(ax,(6.6,2.6),3,1,'Keep record\nconditional state $\\rho_m$')
box(ax,(6.6,.4),3,1,'Discard record\nchannel $\\sum_m M_m\\rho M_m^\\dagger$',coral)
arrow(ax,(2.3,2),(3.1,2)); arrow(ax,(5.5,2.2),(6.5,3)); arrow(ax,(5.5,1.8),(6.5,1))
ax.text(5,0,'Average of entropies and entropy of the average are different.',ha='center',fontsize=11,color=navy)
save(fig,'measurement-map')

fig,ax=plt.subplots(figsize=(8,5.2))
for x in range(8): ax.plot([x,x],[0,6.7],color='#8999a8',lw=1.2)
for t in range(6):
    for x in range(t%2,7,2):
        ax.add_patch(Rectangle((x-.13,t+.3),1.26,.33,facecolor=teal,edgecolor='white',zorder=3))
for x,t in [(0,1),(3,2),(4,3),(6,4),(2,5),(5,1)]:
    ax.add_patch(Circle((x,t+.9),.13,facecolor=coral,zorder=4))
ax.plot([3.5,3.5,2.5,2.5,1.5,1.5],[6.7,5.8,4.8,3.8,2.8,0],color=gold,lw=3,ls='--')
ax.text(3.5,7.02,'Entanglement cut',ha='center',color=gold)
ax.set(xlim=(-.7,7.8),ylim=(-.5,7.5),xlabel='Site',ylabel='Circuit time')
ax.set_yticks([]); ax.text(7.45,3.5,'Time ↑',rotation=90,va='center')
ax.text(.1,-.42,'Teal: two-site gates    Coral: local readouts    Gold: example cut',fontsize=10)
save(fig,'brickwork')

fig,axs=plt.subplots(1,2,figsize=(9,3.6))
l=np.linspace(1,100,200)
axs[0].plot(l,.22*l,color=teal,label='Volume law')
axs[0].plot(l,1.1*np.log(l+1),color=gold,label='Critical logarithm')
axs[0].plot(l,1.8*(1-np.exp(-l/5)),color=coral,label='Area law')
axs[0].set(xlabel='Interval length',ylabel='Entropy (schematic)'); axs[0].legend(frameon=False)
axs[1].axis('off'); box(axs[1],(.02,.64),.88,.23,'Weak monitoring: information hidden')
box(axs[1],(.02,.13),.88,.23,'Strong monitoring: information exposed',coral)
arrow(axs[1],(.46,.60),(.46,.40),'Transition')
fig.tight_layout(); save(fig,'entropy-laws')

rows=list(csv.DictReader((ROOT/'assets/data/circuit_entropy.csv').open()))
data=np.array([[float(r[k]) for k in ['L','p','t','mean_entropy_nats','standard_error']] for r in rows])
fig,axs=plt.subplots(1,2,figsize=(9.5,3.8))
colors=plt.cm.viridis(np.linspace(.05,.9,6))
for p,c in zip([0,.1,.2,.4,.8,1],colors):
    a=data[(data[:,0]==10)&np.isclose(data[:,1],p)]
    axs[0].plot(a[:,2],a[:,3],color=c,label=f'p={p:g}')
    axs[0].fill_between(a[:,2],a[:,3]-a[:,4],a[:,3]+a[:,4],color=c,alpha=.15)
axs[0].set(xlabel='Time (two gate layers + readouts)',ylabel='Half-chain entropy (nats)',title='L = 10; 64 independent trajectories')
axs[0].legend(ncol=2,fontsize=9,frameon=False)
for L,c in zip([6,8,10],[gold,coral,teal]):
    a=data[(data[:,0]==L)&(data[:,2]==60)]
    axs[1].errorbar(a[:,1],a[:,3],yerr=a[:,4],fmt='o-',color=c,capsize=2,label=f'L={L}')
axs[1].set(xlabel='Measurement probability p',ylabel='Entropy at t = 60 (nats)',title='Small systems: illustrative crossover')
axs[1].legend(frameon=False); fig.tight_layout(); save(fig,'circuit-entropy')

fig,axs=plt.subplots(1,2,figsize=(9,3.5))
rng=np.random.default_rng(20261023); eta=.18; n=400
obs=np.where(rng.random(n)<(1+eta)/2,1,-1)
logodds=np.cumsum(obs)*np.log((1+eta)/(1-eta)); posterior=1/(1+np.exp(-logodds))
h=-(posterior*np.log(np.clip(posterior,1e-16,1))+(1-posterior)*np.log(np.clip(1-posterior,1e-16,1)))
axs[0].plot(np.arange(1,n+1),posterior,color=teal); axs[0].axhline(.5,color='#bbb',ls='--'); axs[0].set(xlabel='Number of readouts',ylabel='Posterior probability of z = +1',ylim=(0,1.03))
axs[1].plot(np.arange(1,n+1),h,color=coral); axs[1].set(xlabel='Number of readouts',ylabel='Posterior Shannon entropy (nats)')
fig.tight_layout(); save(fig,'bayesian-collapse')

fig,ax=plt.subplots(figsize=(6.4,4))
k=np.logspace(-3,1,300); D=1.; chi=1.
for gamma,c in zip([.01,.1,1],[gold,coral,teal]):
    # Causal filtering covariance, in the normalization used in Chapter 14.
    v=2*D*chi*k*k/(D*k*k+np.sqrt(D*D*k**4+8*gamma*D*chi*k*k))
    ax.loglog(k,v,color=c,label=f'gamma={gamma:g}')
ax.loglog(k,np.ones_like(k),color='#778899',ls='--',label='Unmonitored')
ax.set(xlabel='Wave number |k|',ylabel='Conditional variance V(k)',title='Gaussian density monitoring: causal filtering')
ax.legend(frameon=False); fig.tight_layout(); save(fig,'conditional-spectrum')

fig,ax=plt.subplots(figsize=(8.2,3.3)); ax.axis('off'); ax.set(xlim=(0,9),ylim=(0,3.3))
box(ax,(.1,1.2),1.6,1,'Reference R',gold); box(ax,(3,1.2),2,1,'Encoded system S')
box(ax,(6.4,2),2.1,.9,'Record / environment E',coral); box(ax,(6.4,.2),2.1,.9,'Surviving output B')
arrow(ax,(1.8,1.7),(2.9,1.7),'Entanglement'); arrow(ax,(5.1,1.9),(6.3,2.4)); arrow(ax,(5.1,1.4),(6.3,.7))
ax.text(4.7,.08,'Recovery requires that E reveal no logical information about R.',ha='center',fontsize=10)
save(fig,'qec-flow')

fig,ax=plt.subplots(figsize=(8,3.5)); ax.axis('off'); ax.set(xlim=(0,8),ylim=(0,3.5))
for y in [.45,2.5]: ax.plot([.5,7.5],[y,y],color=navy,lw=1.2)
ax.plot([2,6],[1.65,1.65],color=coral,lw=5)
ax.text(4,1.95,'Measurement defect on one time slice',ha='center',color=coral)
ax.text(4,.8,'Euclidean critical bulk',ha='center',color=navy)
ax.text(1.9,1.3,'u',ha='center'); ax.text(6.1,1.3,'v',ha='center')
ax.text(4,3.05,'A defect can change scaling without changing the bulk Hamiltonian.',ha='center',fontsize=11)
save(fig,'cft-defect')
