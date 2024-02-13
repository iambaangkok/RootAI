import subprocess
import sys

if __name__ == "__main__":
    procs = []
    for i in range(0, 1):
        config_file_name = 'config-{}-{}.yml'.format(str(i), 'ma' if i < 240 else 'ey')
        print(sys.path[0])
        proc = subprocess.Popen(
            [sys.executable, '-m', 'src.main', './src/config/experiment/{}'.format(config_file_name)])
        procs.append(proc)

    for proc in procs:
        proc.wait()
        
#  Run by using this cmd
#       python -m src.run_experiment