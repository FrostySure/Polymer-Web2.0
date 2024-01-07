import os
import shutil
import re
# Define the list of gases and concentrations
gases = ['H2', 'O2', 'H2O', 'CO2', 'N2']
concentrations = [str(os.getcwd())]
fw_gcmc=open('gcmc_jobs.sh','w')
fw_msd=open('msd_jobs.sh','w')
# Loop through each gas and concentration
for gas in gases:
    for concentration in concentrations:
        # for model in range(5):
            model='P-S-D'
        # Create gas folder if it doesn't exist
            gas_folder = os.path.join(concentration,str(model)+'/'+ gas)
            os.makedirs(gas_folder, exist_ok=True)
            gas_MSD_folder = os.path.join(concentration,str(model)+'/'+ gas+'-MSD')
            os.makedirs(gas_MSD_folder, exist_ok=True)
            source_file = os.path.join(gas, 'in.msd')

            destination_file = os.path.join(gas_MSD_folder, 'in.msd')
            shutil.copy2(source_file, destination_file)
            fw_msd.write('cd '+gas_MSD_folder+'\n')
            fw_msd.write('qsub msd.sh\n')
            # Create subfolders 1-10
            for i in range(1, 11):
                subfolder = os.path.join(gas_folder, str(i))
                os.makedirs(subfolder, exist_ok=True)

                # Copy in.gcmc to the subfolder
                source_file = os.path.join(gas, 'in.gcmc')
                destination_file = os.path.join(subfolder, 'in.gcmc')
                
                shutil.copy2(source_file, destination_file)
                fw_gcmc.write('cd '+subfolder+'\n')
                fw_gcmc.write('qsub gcmc.sh\n')


                # Modify in.gcmc file in subfolder
                with open(destination_file, 'r') as file:
                    lines = file.readlines()

                # Modify the line with 'pressure'
                for j, line in enumerate(lines):
                    if 'pressure' in line:
                        lines[j] = line.replace('10', str(i))

                # Write the modified content back to the file
                with open(destination_file, 'w') as file:
                    file.writelines(lines)

                # Copy additional files *.in.* and {}.txt
                for additional_file in os.listdir(concentration):
                    if re.search(r'gcmc.in.settings', additional_file):
                        shutil.copy2(os.path.join(concentration, additional_file), subfolder)                    
                    if re.search(r'gcmc.sh', additional_file):
                        shutil.copy2(os.path.join(concentration, additional_file), subfolder)
                    if re.search(r'final_300K.data', additional_file):
                        shutil.copy2(os.path.join(concentration, additional_file), subfolder)
                    if re.search(r'{}.txt'.format(gas), additional_file):
                        shutil.copy2(os.path.join(concentration, additional_file), subfolder)
            for additional_file in os.listdir(concentration) :
                if re.search(r'system.in.', additional_file):
                    shutil.copy2(os.path.join(concentration, additional_file), gas_MSD_folder)
                if re.search(r'msd.sh', additional_file):
                    shutil.copy2(os.path.join(concentration, additional_file), gas_MSD_folder)