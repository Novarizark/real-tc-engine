#/usr/bin/env python
'''
Atmospheric Engine to drive the Lagrangian particals
'''

import configparser
import datetime, random, gc
import numpy as np
import xarray as xr
from lib.air_parcel import air_parcel
import core.lagrange

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 


#from wrf import getvar, interplevel, ALL_TIMES 

print_prefix='lib.atm_engine>>'

# Constant Lists
AIRP_HMAX=10000                 # maximum height to generate air partical (m)
AIRP_HMIN=100                 # mininum height to generate air partical (m)

BIGFONT=18
MIDFONT=14
SMFONT=10


class atm_engine:

    '''
    Atmospheric Engine Object 

    Construct, kick-off, and maintain the TC turbo run!

    Attributes
    -----------''' 
    def __init__(self, config, fld):
        """ construct input wrf file names """
        print(print_prefix+'Init...') 

        tc_ix=fld.tc_ix
        tc_iy=fld.tc_iy
        n_radius=fld.n_radius

        self.time_step=int(config['CORE']['time_step'])
        self.num_partical=int(config['CORE']['num_rnd_partical'])
        
        self.stoke_frq_frm=int(int(config['CORE']['stoke_frq'])/self.time_step)
        self.lifetime_frm=int(int(config['CORE']['partical_lifetime'])/self.time_step)
        
        self.glb_ifrm=0

        self.airp_lst=[]

        self.bnd_lats=(fld.xlat.values[tc_ix-n_radius, tc_iy],fld.xlat.values[tc_ix+n_radius, tc_iy])
        self.bnd_lons=(fld.xlon.values[tc_ix, tc_iy-n_radius],fld.xlon.values[tc_ix, tc_iy+n_radius])
        self.box_margin=int(15*(fld.resolution/1000.0)/111.0) # rough in deg


        self.stoke(fld)
 
#--------------- Method: advance -------------------
    def advance(self, cfg, fld):
        ''' Advance the atm engine!'''
        print(print_prefix+'Advance...') 
        u3d=fld.U.values
        v3d=fld.V.values
        w3d=fld.W.values
        z3d=fld.Z.values

        lat2d=fld.xlat.values
        lon2d=fld.xlon.values
        dts = int(cfg['CORE']['time_step'])*60

        for airp in self.airp_lst:
            idx=airp.ix[-1]
            idy=airp.iy[-1]
            idz=airp.iz[-1]
            core.lagrange.lagrange_march(airp, u3d[idz,idx,idy], v3d[idz,idx,idy], w3d[idz,idx,idy], dts)
            core.lagrange.resolve_curr_xyz(airp, lat2d, lon2d, z3d)
        self.glb_ifrm=self.glb_ifrm+1
        
        # runtime add fuel
        if self.glb_ifrm % self.stoke_frq_frm ==0:
            self.stoke(fld, num_partical=
                    int(self.num_partical*self.stoke_frq_frm/self.lifetime_frm))
        # runtime collect cinders
            self.collect_cinders()


#--------------- Method: exhibite -------------------
    def exhibite(self, cfg, iframe):
        ''' Plot the current frame of atmospheric turbo state'''
        
        fn=cfg['OUTPUT']['output_dir']+cfg['OUTPUT']['output_prefix']

        fig = plt.figure(figsize=(16,9), frameon=True)
        ax = fig.gca(projection='3d')

        airp_lat_lst=[ itm.lat[-1] for itm in self.airp_lst]
        airp_lon_lst=[ itm.lon[-1] for itm in self.airp_lst]
        airp_h_lst=[ itm.h[-1] for itm in self.airp_lst]
        airp_init_h_lst=[ itm.h[0] for itm in self.airp_lst]

        ax.scatter( airp_lon_lst, airp_lat_lst, airp_h_lst, c=airp_init_h_lst, cmap='rainbow',vmin=0,vmax=10000, 
                s=6, zorder=1, alpha=0.8)
       
        # below turn off all axis and coordinates labels
        ax.set_facecolor('k')
        plt.axis('off')
        #ax.set_xticks([])
        #ax.set_yticks([])
        #ax.set_zticks([])
        ax.grid(False)

        ax.set_xlim(self.bnd_lons[0], self.bnd_lons[1])
        ax.set_ylim(self.bnd_lats[0], self.bnd_lats[1])
        ax.set_zlim(0, 12000)
        
        plt.title('Real TC Engine @%05dFrm' % iframe, fontsize=MIDFONT)
        plt.savefig('%s.%05dfrm.png' % (fn, iframe) , dpi=80, bbox_inches='tight')

        plt.close('all')
        #plt.show()

       
    def stoke(self, fld, num_partical=0):
        ''' Add fuel to the fire work!'''
        if num_partical==0:
            num_partical=self.num_partical
        tc_ix=fld.tc_ix
        tc_iy=fld.tc_iy
        n_radius=fld.n_radius
        
        # generate air parcels
        for ii in range(0, num_partical):
            ix=tc_ix + get_rnd_ir(n_radius, 'even')
            iy=tc_iy + get_rnd_ir(n_radius, 'even')
            ilev=random.randint(AIRP_HMIN, AIRP_HMAX)
            iz=get_closest_idz(fld.Z.values, ix, iy, ilev)
            ilat=fld.xlat.values[ix,iy]
            ilon=fld.xlon.values[ix,iy]
            self.airp_lst.append(air_parcel(ii, ilat, ilon, ilev, ix, iy, iz))

    def collect_cinders(self):
        ''' Remove cinder from the fire work!'''
        self.airp_lst=[airp for airp in self.airp_lst if airp.iframe != self.lifetime_frm]
        

    def renderer(self, cfg, iframe):
        ''' Render the partical '''
        print(print_prefix+'Exhibite...') 
     

#------------------------------------------
#FUNCTION DEFINATION PART
#------------------------------------------

def get_rnd_ir(radius, kernel):
    """
       generate a sample from (-R,+R) by kernel func
    """
    if kernel=='even':
        x = random.randint(-radius, radius)

    elif kernel=='sigmoid':
        y_smp=random.uniform(0,1)*0.99
        x=int(round(y_smp*radius/6.0))

    elif kernel=='normal':
        x = random.normalvariate(0, 1.0/6.0)*R
        pass
    
    return  x






def get_closest_idz(z3d, ix, iy, zlev):
    """
        Find the nearest z in z3d 
    """
    
    col_z=z3d[:,ix,iy]
    dis=abs(zlev-col_z)
    return np.argmin(dis)




if __name__ == "__main__":
    pass
