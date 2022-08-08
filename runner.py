import os
import sys
import getopt
import multiprocessing
import time
import ctypes as ct

from abg_python.galaxy.gal_utils import Galaxy

def main(savename='m09_res30',suite_name='metal_diffusion',mps=1,**kwargs):

    ## directories for reading in from and outputting new files to
    output_dir = os.path.join(os.environ['HOME'],'scratch','data',suite_name,savename,'chimes')
    
    ## snapshots corresponding to the FIRE-2 public data release
    snaps = [88]#[600, 277, 172, 120, 88][::-1]

    if mps is None: mps = multiprocessing.cpu_count()
    
    print(f'using {mps} threads')
    time.sleep(3)

    for snap in snaps: 
        galaxy = Galaxy(savename,snap,suite_name=suite_name,loud=False,full_init=False,loud_metadata=False)
        try: produce_chimes_output(snap,galaxy.snapdir,output_dir,mps=mps)
        except Exception as e: 
            print(f"{snap} failed: {repr(e)}")
            raise
        
def produce_chimes_output(
    snapnum,
    snapdir,
    output_dir,
    mps=1,
    chimes_driver_dir=None,
    group_output_snapdir=True):

    ## get an array of relevant snapshot files
    input_file = locate_snapshot_files(snapdir,snapnum)

    ## creates an output directory if requested and necessary

    if not os.path.isdir(output_dir): os.makedirs(output_dir)

    output_file = os.path.join(
        output_dir,
        f'chimes_snapshot_{int(snapnum):03d}.hdf5')

    ## generate a parameter file, save it in the datadir
    param_file = create_param_file(input_file,output_file)

    
    ## attempt to import chimes, get an error before we do anything heavy
    try:
        chimesLib = ct.cdll.LoadLibrary(
            os.path.join(os.environ['WORK'],'CHIMES-repos','chimes','libchimes.so'))
    except:
        print("failed to import chimes, make sure it's built")
        raise

    ## change directories to the chimes driver location
    if chimes_driver_dir is None: 
        chimes_driver_dir = os.path.join(
        os.environ['WORK'],
        'CHIMES-repos',
        'chimes-driver')

    current_dir = os.getcwd()
    try:
        os.chdir(chimes_driver_dir)

        ## determine what we're running
        if mps <= 1: exec_str = f"python chimes-driver.py {param_file}"
        else: exec_str = f"mpirun -np {mps} python chimes-driver.py {param_file}"

        os.system(exec_str)

    except: raise
    finally: os.chdir(current_dir)


def locate_snapshot_files(snapdir,snap):
    abs_path = None
    ## find the
    for fname in os.listdir(snapdir):
        if f"{snap:03d}" in fname: 
            abs_path = os.path.join(snapdir,fname)
            break

    if abs_path is None: raise IOError(f"Couldn't find {snap} in {snapdir}")

    #if os.path.isdir(abs_path):
        #sub_snaps = [os.path.join(abs_path,subfile) for subfile in os.listdir(abs_path)]
    #else: sub_snaps = [abs_path]

    return abs_path

def create_param_file(input_file,output_file):
    with open("GIZMO_eqm_template.param",'r') as handle:
        template = handle.read()

    ## Things that need to be replaced in the template:
    ##    chimes_library_path        <CHIMES_DIR>/libchimes.so 
    template = template.replace(
        "<CHIMES_DIR>",
        os.path.join(os.environ['WORK'],'CHIMES-repos','chimes'))
    ##    chimes_data_path           <CHIMES_DATA_DIR>
    template = template.replace(
        "<CHIMES_DATA_DIR>",
        os.path.join(os.environ['WORK'],'CHIMES-repos','chimes-data'))
    ##    input_file 	     	   <INPUT_FILE> 
    template = template.replace("<INPUT_FILE>",input_file)
    ##    output_file                <OUTPUT_FILE>
    template = template.replace("<OUTPUT_FILE>",output_file)

    if '.hdf5' in output_file: param_file = output_file.replace('.hdf5','.param')
    else: param_file = output_file + '.param'
    with open(param_file,'w') as handle: handle.write(template)

    return param_file

if __name__ == '__main__':
    argv = sys.argv[1:]
    opts,args = getopt.getopt(
        argv,'',[
        'savename=',
        'suite_name=',
        'mps='])
    #options:
    #--snap(low/high) : snapshot numbers to loop through
    #--savename : name of galaxy to use
    #--mps : mps flag, default = 0
    for i,opt in enumerate(opts):
        if opt[1]=='':
            opts[i]=('mode',opt[0].replace('-',''))
        else:
            try:
                ## if it's an int or a float this should work
                opts[i]=(opt[0].replace('-',''),eval(opt[1]))
            except:
                ## if it's a string... not so much
                opts[i]=(opt[0].replace('-',''),opt[1])
    main(**dict(opts))
