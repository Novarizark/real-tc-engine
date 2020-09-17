#/usr/bin/env python3
'''
Date: Sep 8, 2020

Main script to drive the real-tc-engine 

Zhenning LI
'''

import numpy as np
import pandas as pd
import  lib.preprocess_wrfinp
from lib.atm_engine import atm_engine
from lib.cfgparser import read_cfg
import os, time

print_prefix='MAIN>>'

def main_run():
    
    print('Real-TC-Engine Start...')
    
    print('Read Config...')
    cfg_hdl=read_cfg('./conf/config.ini')
    
    nsteps= int(cfg_hdl['CORE']['integ_steps'])
    
    print('Init Fields...')
    fields_hdl=lib.preprocess_wrfinp.wrf_acc_fields(cfg_hdl)
    
    print('Ignite Atm Engine...')
    tc_engine=atm_engine(cfg_hdl, fields_hdl)

    tc_engine.exhibite(cfg_hdl, 0)
     
    for istep in range(0, nsteps):
        print(print_prefix+'iStep: %04d/%04d' % (istep, nsteps)) 
        tc_engine.advance(cfg_hdl, fields_hdl)
        tc_engine.exhibite(cfg_hdl, istep) 
    

    os.system('sh control_png_to_gif.sh %d' % (nsteps-1))
    exit()



if __name__=='__main__':
    main_run()
