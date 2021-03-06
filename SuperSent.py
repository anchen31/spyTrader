import os
from multiprocessing import Pool

def run_process(process):                                                             
    os.system('python {}'.format(process))                                                           

#pool.map(run_process, other)                                                 
def main():
    processes = ('TSSmySQL.py', 'RSSmySQL.py', 'Ibpy.py')
    #processes = ('TSSmySQL.py', 'RSSmySQL.py', 'ibStream.py')                                   
    #other = ('stonks.py',)
    pool = Pool(processes=3)                                                        
    pool.map(run_process, processes)

if __name__ == '__main__':
    main()
