import os
import shutil
import re
concentrations = ['10%','20%','30%','40%','50%']
    for concentration in concentrations:
        concentration=os.path.join(str(os.getcwd()),concentration)
        for model in range(5):
            job_dir = os.path.join(concentration,str(model))
            os.system('cp O2.txt add_o2.py '+job_dir)
            subprocess.run('python3 add_o2.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)