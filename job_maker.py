import os
import sys
import getopt
import multiprocessing
import time
import ctypes as ct

from abg_python.galaxy.gal_utils import Galaxy

def main(suite_name='FIRE2_pdr'):

    sim_dir = os.path.join(os.environ['HOME'],'ciera','snaps',suite_name)

    names=[
        'm09_res30',
        'm10q_res30',
        'm10v_res30',
        'm11b_res2100',
        'm11d_res7100',
        'm11e_res7100',
        'm11h_res7100',
        'm11i_res7100',
        'm11q_res880',
        'm12m_res7100',
        'm12z_res4200',
        'm12b_res7100',
        'm12c_res7100',
        'm12f_res7100',
        'm12i_res7100',
        'm12r_res7100',
        'm12w_res7100',
        'm12_elvis_RomulusRemus_res4000',
        'm12_elvis_RomeoJuliet_res3500',
        'm12_elvis_ThelmaLouise_res4000']

    names = os.listdir(sim_dir)
    #snapnums=[600,277,172,120,88]
    snapnums = None

    mps = multiprocessing.cpu_count()
    
    print(f'using {mps} threads')
    time.sleep(3)
    
    for savename in names:
        ## directories for reading in from and outputting new files to
        snapdir = os.path.join(sim_dir,savename,'output')
        datadir = os.path.join(os.environ['HOME'],'ciera','data',suite_name,savename,'chimes')

        ## which snapshots to run on
        if snapnums is None:
            snapnums = sorted([int(fname.split('_')[1].split('.hdf5')[0]) for fname in os.listdir(snapdir)])

        for snapnum in snapnums:
            galaxy = Galaxy(
                savename,
                snapnum,
                suite_name=suite_name,
                snapdir=snapdir,
                datadir=datadir,
                loud=False,
                full_init=False,
                loud_metadata=False)

            try: 
                produce_chimes_output(
                    snapnum,
                    galaxy.snapdir,
                    galaxy.datadir,
                    mps=mps)
            except Exception as e: print(f"{snapnum} failed: {repr(e)}"); raise
        
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
            os.path.join(
                os.environ['HOME'],
                'projects',
                'chimes_dirs',
                'chimes',
                'libchimes.so'))
    except:
        print("failed to import chimes, make sure it's built")
        raise

    ## change directories to the chimes driver location
    if chimes_driver_dir is None: 
        chimes_driver_dir = os.path.join(
            os.environ['HOME'],
            'projects',
            'chimes_dirs',
            'chimes-driver')

    current_dir = os.getcwd()
    if not os.path.isfile(outputfile):
        try:
            #os.chdir(chimes_driver_dir)

            ## determine what we're running
            if mps <= 1: exec_str = f"python chimes-driver.py {param_file}"
            else: exec_str = f"mpirun -npernode {mps} --bind-to-core python chimes-driver.py {param_file}"

            jobfile = os.path.join(current_dir,'submission_scripts')
            name = os.path.basename(os.path.dirname(snapdir))
            if not os.path.isdir(jobfile): os.makedirs(jobfile)
            jobfile = os.path.join(jobfile,f'{name}_{snapnum:03d}.sh')
            with open('preamble.sh','r') as rhandle:
                with open(jobfile,'w') as whandle:
                    whandle.write(rhandle.read())
                    whandle.write(f"#SBATCH -J {name}_{snapnum}_chimes\n")
                    whandle.write(f"cd {chimes_driver_dir}\n")
                    whandle.write(exec_str+"\n")
            #os.system(exec_str)

        except: raise
    else: print(outputfile,'exists. will not generate a submission script')
    #finally: os.chdir(current_dir)


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
        os.path.join(
            os.environ['HOME'],
            'projects',
            'chimes_dirs',
            'chimes'))

    ##    chimes_data_path           <CHIMES_DATA_DIR>
    template = template.replace(
        "<CHIMES_DATA_DIR>",
        os.path.join(
            os.environ['HOME'],
            'projects',
            'chimes_dirs',
            'chimes-data'))
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
        'snapnum=',
        'savename=',
        'suite_name=',
        'mps='])
    #options:
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
