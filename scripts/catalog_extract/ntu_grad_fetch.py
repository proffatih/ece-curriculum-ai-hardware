import sys
sys.path.insert(0, 'raw/_scripts')
from catv2 import fetch
B='https://www.ntu.edu.sg/engineering/coe-programmes/graduate/coe-programme-detail/'
P=['master-of-science-in-communications-engineering','master-of-science-in-computer-control-automation',
'master-of-science-in-integrated-circuits-and-microelectronics','master-of-science-in-power-engineering',
'master-of-science-in-signal-processing','joint-master-of-science-in-green-electronics','joint-master-of-science-in-ic-design',
'eee-doctor-of-philosophy-(ph.d)-programme']
for p in P:
    t,ts=fetch('ntu',B+p,'grad__'+p.replace('(','').replace(')','')+'.html')
    print(p,len(t),ts, t.count('EE6'), t.count('EE7'), t.count('EE5'))
