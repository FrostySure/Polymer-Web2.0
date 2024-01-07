fr = open('anneal.log', 'r')
fw = open('density.txt', 'w')
# n_start=0
n_list_start = []
# n_end=0
n_list_end = []
n = 0
data_start = 'Step Temp PotEng Volume Density TotEng Lx Ly Lz'
data_end = 'Loop time of'
for line in fr:
    if data_start in line:
        n_list_start.append(n)

    elif data_end in line:
        n_list_end.append(n)
        # print(line)

    n += 1
density_list = []
fr.close()
for i in range(len(n_list_start)):
    fr = open('anneal.log')
    density = 0
    for line in fr.readlines()[n_list_end[i]-100:n_list_end[i]]:
        # print(line)
        line = line.split(' ')
        strings = []
        for string in line:
            if string:
                strings.append(string)
        # print(strings)

        density += float(strings[4])
    avg_density = density/(100)
    density_list.append(avg_density)
    fr.close()

for density in density_list:
    fw.write(str(density)+' \n')
fr=open('density.txt','r')
fw=open('Tg.txt','w')
i=1
for line in fr:
   #print(line)
   if i%2==0:
      fw.write(line)
   i+=1
fr.close()
fw.close()
fr=open('Tg.txt','r')
density=[]
for line in fr:
    print(line)
    line.strip('\n')
    density.append(float(line))
num=0
Tg={}
T=500
for num in range(len(density)):
  if num < len(density)-1:
    #print(density[num+1]-density[num],T)
    #Tg.append(density[num+1]-density[num],T)
    T=T-20
