import os                                                                       
from multiprocessing import Pool                                                
                                                                                
                                                                                
processes = ('TSSmySQL.py', 'process2.py')                                    
other = ('process3.py',)
                                                  
                                                                                
def run_process(process):                                                             
    os.system('python {}'.format(process))                                       
                                                                                
                                                                                
pool = Pool(processes=3)                                                        
pool.map(run_process, processes) 
pool.map(run_process, other) 