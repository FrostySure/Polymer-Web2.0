import os
import shutil
import re
# Define the list of gases and concentrations
gases = ['H2', 'O2', 'H2O', 'CO2', 'N2']
concentrations = ['10%','20%','30%','40%','50%']

# Loop through each gas and concentration
for gas in gases:
    for concentration in concentrations:
        concentration=os.path.join(str(os.getcwd()),concentration)

        for model in range(5):
            model=str(model)+'/P-S-D'
        # Create gas folder if it doesn't exist
            gas_folder = os.path.join(concentration,str(model)+'/'+ gas)
            gas_MSD_folder = os.path.join(concentration,str(model)+'/'+ gas+'-MSD')

            # Create subfolders 1-10
            for i in range(10, 11):
                subfolder = os.path.join(gas_folder, str(i))
                source_file = os.path.join(subfolder, 'last.data')
                destination_file = os.path.join(gas_MSD_folder, 'last.data')
                shutil.copy2(source_file, destination_file)





