import codecs
import os

class Cal_gas():
    def __init__(self, path=os.getcwd()+'/', start=1, end=11, gas_list=['H2', 'O2', 'H2O', 'CO2', 'N2']):
        self.path = path
        self.start = start
        self.end = end
        self.gas_list = gas_list

    def cal_gcmc(f):

        n = 0
        m = 0
        for line in f.readlines()[:-1]:
            if line != '\n':
                a = line.split()
                b = a[0]  # where to read
                if str(b) == str(500000+10*n):
                    n = n+1
                    m = m + int(a[-2])

        f.close()
        #num=0
        #if n != 0: 
        number = m/n
        #number=num
        #vol = 2.334*number
        vol = number/2
        return vol

    def cal_gas(self):
        fw = open('vol.txt', 'w')
        fw_1 = open('number.txt','w')
        fw_2 = open('avg.txt','w')
        fw_3 = open('avg_vol.txt','w')
        gases = ['H2', 'O2', 'H2O', 'CO2', 'N2']
        concentrations = ['10%','20%','30%','40%','50%']

        # Loop through each gas and concentration
        for gas in gases:

            for concentration in concentrations:
               #avg_number=[]
               concentration=os.path.join(str(os.getcwd()),concentration)
               for i in range(1,11):
                avg_number=[]   
                avg_vol=[]   
                for model in range(5):
                     model=str(model)+'/P-S-D'
        # Create gas folder if it doesn't exist
                     gas_folder = os.path.join(concentration,str(model)+'/'+ gas)
#                   for i in range(1,11):
                     subfolder = os.path.join(gas_folder, str(i))
                     source_file = os.path.join(subfolder, 'gcmc.log')
                     data_source_file = os.path.join(subfolder, 'last.data')
                     if os.path.exists(data_source_file):
                        with open(data_source_file, 'r') as data_file:
                            for line in data_file:
                                if 'xlo' in line:
                                    xlo, xhi = map(float, line.split()[:2])
                                    x=xhi-xlo
                                elif 'ylo' in line:
                                    ylo, yhi = map(float, line.split()[:2])
                                    y=yhi-ylo
                                elif 'zlo' in line:
                                    zlo, zhi = map(float, line.split()[:2])
                                    z=zhi-zlo

                     last_log = source_file
                     if os.path.exists(last_log):
                        f = codecs.open(last_log, mode='r', encoding='utf-8')
                    
                        vol = Cal_gas.cal_gcmc(f)
                        number=vol
                        avg_number.append(number)
                        vol = vol*8.314*273 
                        vol = vol/(6.02*101325*(x*y*z))
                        vol = vol*10000000
                        vol = float('%.4g' % vol)
                        avg_vol.append(vol)
                        # if i == 1:
                        #     fw.write(gas+'\n'+str(vol)+'\n')
                        # else:
                        #     fw.write(str(vol) + '\n')
                        # if i == 1:
                        #     fw_1.write(gas+'\n'+str(number)+'\n')
                        # else:
                        #     fw_1.write(str(number) + '\n')

                        f.close()
                fw_2.write(str(sum(avg_number)/len(avg_number))+'\t')
                avg_number.sort()
                fw_2.write(str(avg_number[-1]-(sum(avg_number)/len(avg_number)))+'\t')
                fw_2.write(str(avg_number[0]-(sum(avg_number)/len(avg_number)))+'\t\n')

                fw_3.write(str(sum(avg_vol)/len(avg_vol))+'\t')
                avg_vol.sort()
                fw_3.write(str(avg_vol[-1]-(sum(avg_vol)/len(avg_vol)))+'\t')
                fw_3.write(str(avg_vol[0]-(sum(avg_vol)/len(avg_vol)))+'\t\n')
demo_cal = Cal_gas()
demo_cal.cal_gas()
