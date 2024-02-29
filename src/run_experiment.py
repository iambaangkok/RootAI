import subprocess
import sys
import time
import datetime
from datetime import datetime, timedelta

ALL_CONFIGS_FILE = 216
BATCH_SIZE = 20
SPECIFIC_FILE = [102, 107, 177, 208, 215]

if __name__ == "__main__":
    procs = []
    completed = 0
    file = open('src/elapsed_time-{}.txt'.format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")), 'w')
    
    start_time = time.time()
    
    if not SPECIFIC_FILE: 
        while completed < ALL_CONFIGS_FILE:
            start_time_batch = time.time()
            
            for i in range(completed, completed + BATCH_SIZE):
                if i >= ALL_CONFIGS_FILE:
                    continue
                config_file_name = 'config-{}-{}.yml'.format(str(i), 'ma' if i < (ALL_CONFIGS_FILE/2) else 'ey')
                proc = subprocess.Popen(
                    [sys.executable, '-m', 'src.main', './src/config/experiment/{}'.format(config_file_name)])
                procs.append(proc)

            for proc in procs:
                proc.wait()
            
            completed += BATCH_SIZE
            completed = min(completed, ALL_CONFIGS_FILE)
            now = time.time()
            print(
                "Run {}/{} | Elapsed time: {} | Total time: {} | Estimated remaining time: {}\n".format(
                completed, ALL_CONFIGS_FILE 
                , str(timedelta(seconds = now-start_time_batch))
                , str(timedelta(seconds = now-start_time))
                , str(timedelta(seconds = ((now-start_time)/completed) * (ALL_CONFIGS_FILE - completed)))
                )
            )
            file.write("Run {}/{} | Elapsed time: {} | Total time: {} | Estimated remaining time: {}\n".format(
                completed, ALL_CONFIGS_FILE 
                , str(timedelta(seconds = now-start_time_batch))
                , str(timedelta(seconds = now-start_time))
                , str(timedelta(seconds = ((now-start_time)/completed) * (ALL_CONFIGS_FILE - completed)))
                ))
    else:
        while completed < len(SPECIFIC_FILE):
            start_time_batch = time.time()
            
            for i in SPECIFIC_FILE:
                if i >= ALL_CONFIGS_FILE:
                    continue
                config_file_name = 'config-{}-{}.yml'.format(str(i), 'ma' if i < (ALL_CONFIGS_FILE/2) else 'ey')
                print("Running " + config_file_name)
                proc = subprocess.Popen(
                    [sys.executable, '-m', 'src.main', './src/config/experiment/{}'.format(config_file_name)])
                procs.append(proc)

            for proc in procs:
                proc.wait()
            
            completed += BATCH_SIZE
            completed = min(completed, len(SPECIFIC_FILE))
            now = time.time()
            print(
                "Run {}/{} | Elapsed time: {} | Total time: {} | Estimated remaining time: {}\n".format(
                completed, ALL_CONFIGS_FILE 
                , str(timedelta(seconds = now-start_time_batch))
                , str(timedelta(seconds = now-start_time))
                , str(timedelta(seconds = ((now-start_time)/completed) * (ALL_CONFIGS_FILE - completed)))
                )
            )
            file.write("Run {}/{} | Elapsed time: {} | Total time: {} | Estimated remaining time: {}\n".format(
                completed, ALL_CONFIGS_FILE 
                , str(timedelta(seconds = now-start_time_batch))
                , str(timedelta(seconds = now-start_time))
                , str(timedelta(seconds = ((now-start_time)/completed) * (ALL_CONFIGS_FILE - completed)))
                ))
        
#  Run by using this cmd
#       python -m src.run_experiment