#/usr/bin/env python
"""Preprocessing the WRF input file"""

import configparser
import datetime
import numpy as np
import xarray as xr
import gc

from netCDF4 import Dataset
import wrf
#from wrf import getvar, interplevel, ALL_TIMES 

print_prefix='lib.preprocess_wrfinp>>'

class wrf_acc_fields:

    '''
    Construct and accumulate U V W field 
    

    Attributes
    -----------
    wrf_dt: int
        input data frq from wrf raw input file(s), in seconds
    U: float
    V: float
    W: float

    Methods
    '''
    
    def __init__(self, config):
        """ construct input wrf file names """
    
        self.ncfile=Dataset(config['INPUT']['input_fn'])
        self.resolution=float(wrf.extract_global_attrs(self.ncfile, 'DX')['DX'])
        
        n_radius = int(int(config['INPUT']['vis_radius'])/int(self.resolution))
        
        times_dt64=wrf.getvar(self.ncfile, 'Times',timeidx=wrf.ALL_TIMES, method="cat").values
        self.tgt_timeframe=datetime.datetime.strptime(config['INPUT']['vis_timestamp'],'%Y%m%d%H%M%S')
        print(print_prefix+'Selected Timeframe:%s' % self.tgt_timeframe.strftime('%Y-%m-%d_%H:%M:%S'))
        
        # get idx of the field will be extract
        tgt_times_dt64= np.datetime64(self.tgt_timeframe) 
        t_idx=np.where(times_dt64==tgt_times_dt64)[0][0] 
        
        print(print_prefix+'init from single input file for lat2d, lon2d, and hgt')
        self.xlat = wrf.getvar(self.ncfile, 'XLAT')
        self.xlon = wrf.getvar(self.ncfile, 'XLONG')
        
        print(print_prefix+'init from single input file for Z4d')
        self.SLP= wrf.getvar(self.ncfile, 'slp',timeidx=t_idx)
        
        self.tc_ix, self.tc_iy = find_tc_center(self.SLP)

        print(print_prefix+'init from single input file for Z4d')
        self.Z= wrf.getvar(self.ncfile, 'z',timeidx=t_idx)
        
        print(print_prefix+'init from single input file for U4d')
        self.U = wrf.getvar(self.ncfile, 'ua',timeidx=t_idx)
        
        print(print_prefix+'init from single input file for V4d')
        self.V = wrf.getvar(self.ncfile, 'va',timeidx=t_idx)
        
        print(print_prefix+'init from single input file for W4d')
        self.W = wrf.getvar(self.ncfile, 'wa',timeidx=t_idx)


        print(print_prefix+'init multi files successfully!')


def find_tc_center(slp):
    '''
    function to find the tc centr in 2D slp field
    '''



if __name__ == "__main__":
    pass
