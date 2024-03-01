import subprocess
import sys
import time
from datetime import datetime, timedelta

ALL_CONFIGS_FILE = 25
BATCH_SIZE = 25

if __name__ == "__main__":
    procs = []
    completed = 0
    file = open('src/experiment_2-elapsed_time-{}.txt'.format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")), 'w')

    start_time = time.time()

    while completed < ALL_CONFIGS_FILE:
        start_time_batch = time.time()

        for i in range(completed, completed + BATCH_SIZE):
            if i >= ALL_CONFIGS_FILE:
                continue
            config_file_name = 'config-final-{}.yml'.format(str(i))
            proc = subprocess.Popen(
                [sys.executable, '-m', 'src.main', './src/config/experiment_2/{}'.format(config_file_name)])
            procs.append(proc)

        for proc in procs:
            proc.wait()

        completed += BATCH_SIZE
        completed = min(completed, ALL_CONFIGS_FILE)
        now = time.time()
        print(
            "Run {}/{} | Elapsed time: {} | Total time: {} | Estimated remaining time: {}\n".format(
                completed, ALL_CONFIGS_FILE
                , str(timedelta(seconds=now - start_time_batch))
                , str(timedelta(seconds=now - start_time))
                , str(timedelta(seconds=((now - start_time) / completed) * (ALL_CONFIGS_FILE - completed)))
            )
        )
        file.write("Run {}/{} | Elapsed time: {} | Total time: {} | Estimated remaining time: {}\n".format(
            completed, ALL_CONFIGS_FILE
            , str(timedelta(seconds=now - start_time_batch))
            , str(timedelta(seconds=now - start_time))
            , str(timedelta(seconds=((now - start_time) / completed) * (ALL_CONFIGS_FILE - completed)))
        ))


#  Run by using this cmd
#       python -m src.run_experiment