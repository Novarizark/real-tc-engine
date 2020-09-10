#/usr/bin/env python3
'''
Date: Sep 8, 2020

Main script to drive the real-tc-engine 

Zhenning LI
'''

import numpy as np
import pandas as pd
import  lib.preprocess_wrfinp
from lib.cfgparser import read_cfg
import os, time



def main_run():
    
    itsk=0
    print('Real-TC-Engine Start...')
    
    print('Read Config...')
    cfg_hdl=read_cfg('./conf/config.ini')
    
    print('Init Fields...')
    fields_hdl=lib.preprocess_wrfinp.wrf_acc_fields(cfg_hdl)

    exit()


if __name__=='__main__':
    main_run()
