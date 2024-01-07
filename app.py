import os
from flask import redirect
import subprocess
from flask import Flask, render_template, jsonify, request, url_for
import tempfile
import threading
import time
from flask_socketio import SocketIO, emit




app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'secret_key'  
socketio = SocketIO(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSONIFY_MIMETYPE'] = 'application/json;charset=utf-8'
top_output = []  
jobs = []  

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/tasks")
def tasks():
    return render_template('tasks.html')

@app.route("/community")
def community():
    return render_template('community.html')

@app.route("/news")
def news():
    return render_template('news.html')

@app.route('/views')
def views():
    return render_template('views.html')

@app.route('/job_state')
def job_state():
    global jobs
    return render_template('job_state.html', jobs=jobs)

@app.route('/top_state')
def top_state():
    global jobs
    return render_template('top_state.html', jobs=jobs)

@app.route('/get_top_output')
def get_top_output():
    return jsonify({'top_output': top_output})

@socketio.on('connect', namespace='/job_state')
def connect_job_state():
    threading.Thread(target=run_top_command).start()

def run_top_command():
    global top_output
    process = subprocess.Popen(['top'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in process.stdout:
        top_output.append(line.strip())
        socketio.emit('top_output', {'line': line.strip()}, namespace='/job_state')  # 发送输出信息给客户端
    process.stdout.close()

def update_job_status(job_dir, status):
    for job in jobs:
        if job['job_dir'] == job_dir:
            job['status'] = status
            break

def process_job(job_dir, ncore, outfilename, filename, npoly, linkatom, nchain, lbox, step, annealing,
                rise_step, rise_equil_step, down_step, down_equil_step, anneal_tmp_start, anneal_tmp_down):
    try:
        max_attempts = 100  # 最大尝试次数
        attempt = 1

        while attempt <= max_attempts:
            try:
                subprocess.run('python simple_polymer_model.py', check=True, shell=True, timeout=10, cwd=job_dir)
                # 命令成功执行，退出循环
                break
            except subprocess.TimeoutExpired:
                if attempt < max_attempts:
                    # 命令执行失败，重新尝试
                    print(f'Command failed, retrying (attempt {attempt}/{max_attempts})')
                    attempt += 1
                    # 增加延迟等待后再次尝试
                    time.sleep(2)
                else:
                    # 达到最大尝试次数，抛出异常或执行其他操作
                    print('Command failed after maximum attempts')
                    raise

        # 将输出重定向到文件
        log_pwd = os.path.join(job_dir, 'moltemplate_output.txt')
        with open(log_pwd, 'w') as output_file:
            subprocess.run('moltemplate.sh tes' + str(npoly) + '.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            update_job_status(job_dir, 'disorder单链模型建模完成，正在进行disorder单链弛豫')  # 更新作业状态为完成

        log_pwd = os.path.join(job_dir, 'order_output.txt')
        with open(log_pwd, 'w') as output_file:
            subprocess.run('python write_pure_packmol.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
        print('Job', job_dir, 'has been modeled')

        lmp_log_pwd = os.path.join(job_dir, 'dis_equil.log')
        with open(lmp_log_pwd, 'w') as output_file:
            subprocess.run('python dis_equil.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            subprocess.run('python dis_equil2.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < dis_equil.in', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < dis_equil2.in', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            update_job_status(job_dir, 'disorder单链弛豫完成，正在进行disorder整体建模')  # 更新作业状态为完成

        lmp_log_pwd = os.path.join(job_dir, 'packmol.log')
        with open(lmp_log_pwd, 'w') as output_file:
            subprocess.run('python dcd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)   
            subprocess.run('python data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)        
            subprocess.run('packmol < packmol.in > packmol.log ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)        
            subprocess.run('moltemplate.sh -pdb system.pdb system.lt ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)     
            update_job_status(job_dir, 'disorder模型整体建模完成，正在进行disorder模型退火计算')  # 更新作业状态为完成


#模型整体退火            
        lmp_log_pwd = os.path.join(job_dir, 'anneal.log')
        with open(lmp_log_pwd, 'w') as output_file:
            subprocess.run('python anneal.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < anneal.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            subprocess.run('python get_Tg.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            update_job_status(job_dir, 'disorder模型力学退火完成，正在进行disorder模型FFV、PSD计算')  # 更新作业状态为完成

#disorder模型孔径分布、孔隙率
        lmp_log_pwd = os.path.join(job_dir, 'FFV-PSD.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:

                    subprocess.run('python chat_data2cif.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -psd 0  100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -volpo  0 100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    # subprocess.run('python get_FFV_PSD.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'disorder模型FFV、PSD计算完成，正在进行disorder模型力学性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'disorder模型FFV、PSD计算建模失败')  # 更新作业状态为失败
#disorder模型力学性质
        lmp_log_pwd = os.path.join(job_dir, 'deform.txt')
        with open(lmp_log_pwd, 'w') as output_file:  
            try:
                subprocess.run('python deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < deform.in > deform.log', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                # subprocess.run('python get_deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'disorder模型力学性质计算完成，正在进行disorder模型渗透性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'disorder模型力学性质计算失败')  # 更新作业状态为失败
#disorder模型渗透性质
        lmp_log_pwd = os.path.join(job_dir, 'Peameation.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:


                    subprocess.run('python cp_gcmc.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
        #提交gcmc作业
                    subprocess.run('sh gcmc_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'disorder模型渗透性质--吸附性质计算完成，正在进行disorder模型渗透性质--扩散计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'disorder模型渗透性质--吸附性质计算失败')  # 更新作业状态为失败
    #复制last.data
            try:
                subprocess.run('python cp_msd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('sh msd_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'disorder模型渗透性质--扩散性质计算完成，正在进行最后处理')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'disorder模型渗透性质--扩散性质计算失败')  # 更新作业状态为失败
            # subprocess.run('python get_P_D_S.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)

        update_job_status(job_dir, '完成')  # 更新作业状态为完成
        socketio.emit('job_finished', {'job_dir': job_dir}, namespace='/job_state')  # 发送任务完成事件给客户端
        
    except subprocess.CalledProcessError:
        update_job_status(job_dir, '失败')  # 更新作业状态为失败

def process_crystal_job(job_dir, ncore, outfilename, filename, npoly, linkatom, nchain, lbox, step, annealing,
                rise_step, rise_equil_step, down_step, down_equil_step, anneal_tmp_start, anneal_tmp_down):
    try:
        max_attempts = 100  # 最大尝试次数
        attempt = 1

        while attempt <= max_attempts:
            try:
                subprocess.run('python crystal_polymer_model.py', check=True, shell=True, timeout=3, cwd=job_dir)
                
                # 命令成功执行，退出循环
                break
            except subprocess.TimeoutExpired:
                if attempt < max_attempts:
                    # 命令执行失败，重新尝试
                    print(f'Command failed, retrying (attempt {attempt}/{max_attempts})')
                    attempt += 1
                    # 增加延迟等待后再次尝试
                    time.sleep(2)
                else:
                    # 达到最大尝试次数，抛出异常或执行其他操作
                    print('Command failed after maximum attempts')
                    raise

        # 将输出重定向到文件
        # 将输出重定向到文件


        log_pwd = os.path.join(job_dir, 'order_output.txt')
        with open(log_pwd, 'w') as output_file:
            #规则高分子整体建模
            subprocess.run('moltemplate.sh order_system.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            #根据规则高分子建模构建适合的无定形模型
            subprocess.run('python get_data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            print('Job', job_dir, 'has been modeled')
            update_job_status(job_dir, 'order模型建模完成，正在进行order模型退火计算')  # 更新作业状态为完成



#order模型整体退火            
        lmp_log_pwd = os.path.join(job_dir, 'anneal.log')
        with open(lmp_log_pwd, 'w') as output_file:
            subprocess.run('python order_anneal.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < anneal.in > anneal.log', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            subprocess.run('python get_Tg.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            update_job_status(job_dir, 'order模型退火计算完成，正在进行order模型FFV、PSD计算')  # 更新作业状态为完成

#order模型孔径分布、孔隙率
        lmp_log_pwd = os.path.join(job_dir, 'FFV-PSD.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:

                    subprocess.run('python chat_data2cif.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -psd 0  100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -volpo  0 100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    # subprocess.run('python get_FFV_PSD.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'order模型FFV、PSD计算完成，正在进行order模型力学性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'order模型FFV、PSD计算建模失败')  # 更新作业状态为失败
#order模型力学性质
        lmp_log_pwd = os.path.join(job_dir, 'deform.txt')
        with open(lmp_log_pwd, 'w') as output_file:  
            try:
                subprocess.run('python order_deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < deform.in > deform.log', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                # subprocess.run('python get_deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'order模型力学性质计算完成，正在进行order模型渗透性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'order模型力学性质计算失败')  # 更新作业状态为失败
#order模型渗透性质
        lmp_log_pwd = os.path.join(job_dir, 'Peameation.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:


                    subprocess.run('python cp_gcmc.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
        #提交gcmc作业
                    subprocess.run('sh gcmc_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'order模型渗透性质--吸附性质计算完成，正在进行order模型渗透性质--扩散计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'order模型渗透性质--吸附性质计算失败')  # 更新作业状态为失败
    #复制last.data
            try:
                subprocess.run('python cp_msd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('sh msd_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'order模型渗透性质--扩散性质计算完成，正在进行最后处理')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'order模型渗透性质--扩散性质计算失败')  # 更新作业状态为失败
            # subprocess.run('python get_P_D_S.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)

        update_job_status(job_dir, '完成')  # 更新作业状态为完成
        socketio.emit('job_finished', {'job_dir': job_dir}, namespace='/job_state')  # 发送任务完成事件给客户端
        
    except subprocess.CalledProcessError:
        update_job_status(job_dir, '失败')  # 更新作业状态为失败

def process_semi_job(job_dir, ncore, outfilename, filename, npoly, linkatom, order_nchain, disorder_nchain,lbox, step, annealing,
                rise_step, rise_equil_step, down_step, down_equil_step, anneal_tmp_start, anneal_tmp_down):
    try:
        max_attempts = 100  # 最大尝试次数
        attempt = 1
        while attempt <= max_attempts:
                
            try:
                subprocess.run('python semi_polymer_model.py', check=True, shell=True, timeout=60, cwd=job_dir)
                update_job_status(job_dir, '初始文件准备完毕,正在进行无定形高分子单链建模')  # 更新作业状态为完成
                break 
            # 命令成功执行，退出循环
            except subprocess.TimeoutExpired:
                if attempt < max_attempts:
                    # 命令执行失败，重新尝试
                    print(f'Command failed, retrying (attempt {attempt}/{max_attempts})')
                    update_job_status(job_dir, f'初始文件准备再次尝试，尝试次数：{attempt}/{max_attempts})')  # 更新作业状态为失败
                    attempt += 1
                    # 增加延迟等待后再次尝试
                    time.sleep(2)
                else:
                    # 达到最大尝试次数，抛出异常或执行其他操作
                    print('Command failed after maximum attempts')
                    raise
            except subprocess.CalledProcessError:
                update_job_status(job_dir, '初始文件准备失败')  # 更新作业状态为失败
        # 将输出重定向到文件
        log_pwd = os.path.join(job_dir, 'moltemplate_output.txt')
        try:
            with open(log_pwd, 'w') as output_file:

                # 通过空格分割字符串
                numbers = npoly.split()

                # 将字符串转换为整数
                npoly = [int(num) for num in numbers]
                #无定形高分子单链建模
                all_poly=0
                if len(npoly)>1:
                    for poly in npoly:
                        # poly = int(poly)
                        if poly != ' ':
                            all_poly+=int(poly)
                    if all_poly!=npoly:
                        all_poly+=2    
                        npoly=all_poly
                # print(str(npoly))
                subprocess.run('moltemplate.sh tes' + str(npoly) + '.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)


                update_job_status(job_dir, '无定形高分子单链建模完成,正在进行规则高分子整体建模')  # 更新作业状态为完成
        except subprocess.CalledProcessError:
            update_job_status(job_dir, '无定形高分子单链建模失败')  # 更新作业状态为失败
        log_pwd = os.path.join(job_dir, 'order_output.txt')
        with open(log_pwd, 'w') as output_file:
            try:

                #规则高分子整体建模
                subprocess.run('moltemplate.sh order_system.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                # subprocess.run('python write_system_lt.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                #根据规则高分子建模构建适合的无定形模型
                update_job_status(job_dir, '规则高分子建模完成,正在进行无定形高分子单链弛豫')  # 更新作业状态为完成

                subprocess.run('python get_data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('python write_disorder_packmol.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            except subprocess.CalledProcessError:
                update_job_status(job_dir, '规则高分子单链建模失败')  # 更新作业状态为失败
        lmp_log_pwd = os.path.join(job_dir, 'dis_equil.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:
                #无定形高分子单链弛豫
                subprocess.run('python dis_equil.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('python dis_equil2.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < dis_equil.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < dis_equil2.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, '无定形高分子单链弛豫完成，正在进行无定形高分子整体建模')  # 更新作业状态为完成
            except subprocess.CalledProcessError:
                update_job_status(job_dir, '无定形高分子单链弛豫失败')  # 更新作业状态为失败
        lmp_log_pwd = os.path.join(job_dir, 'packmol.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:
                
                    #无定形高分子整体建模
                subprocess.run('python dcd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)   
                subprocess.run('python data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)        
                subprocess.run('packmol < packmol.in  ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)   
                subprocess.run('python system_box.py  ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)   
                subprocess.run('moltemplate.sh -pdb system.pdb system.lt  ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)          
                update_job_status(job_dir, '无定形高分子整体建模完成，正在进行无定形高分子整体弛豫')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, '无定形高分子整体建模失败')  # 更新作业状态为失败
# 无定形整体弛豫   
        lmp_log_pwd = os.path.join(job_dir, 'dis_sys_equil.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:
                
                subprocess.run('python dis_sys_equil.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < dis_sys_equil.in > dis_sys_equil.log', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, '无定形高分子整体弛豫完成，正在进行semi模型整体建模')  # 更新作业状态为完成

                subprocess.run('python dis_dcd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)   
                subprocess.run('python dis_data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file) 
                #subprocess.run('moltemplate.sh order_system.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)

                subprocess.run('python order_data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file) 
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, '无定形高分子整体弛豫失败')  # 更新作业状态为失败
    #semi模型整体建模并弛豫
        lmp_log_pwd = os.path.join(job_dir, 'all_sys_equil.txt')
        with open(lmp_log_pwd, 'w') as output_file:
                try:
                    subprocess.run('python sys_lt.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('python sys_packmol.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('packmol < sys_packmol.in  ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file) 
                    subprocess.run('moltemplate.sh -pdb all_sys.pdb all_sys.lt ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)     
                    update_job_status(job_dir, 'semi模型整体建模完成，正在进行semi模型整体退火')  # 更新作业状态为完成
                except subprocess.CalledProcessError or 'ERROR' in output_file:
                    update_job_status(job_dir, 'semi模型整体建模失败')  # 更新作业状态为失败
#semi模型整体退火            
                try:
                    subprocess.run('python all_sys.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < anneal.in > anneal.log ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型整体退火完成，正在进行semi模型Tg')  # 更新作业状态为完成
                except subprocess.CalledProcessError or 'ERROR' in output_file:
                    update_job_status(job_dir, 'semi模型整体退火失败')  # 更新作业状态为失败
                try:
                    subprocess.run('python get_Tg.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型Tg计算完成，正在进行semi模型FFV、PSD计算')  # 更新作业状态为完成
                except subprocess.CalledProcessError or 'ERROR' in output_file:
                    update_job_status(job_dir, 'semi模型Tg计算失败')  # 更新作业状态为失败
#semi模型孔径分布、孔隙率
        lmp_log_pwd = os.path.join(job_dir, 'FFV-PSD.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:

                    subprocess.run('python chat_data2cif.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -psd 0  100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -volpo  0 100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    # subprocess.run('python get_FFV_PSD.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型FFV、PSD计算完成，正在进行semi模型力学性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型FFV、PSD计算建模失败')  # 更新作业状态为失败
#semi模型力学性质
        lmp_log_pwd = os.path.join(job_dir, 'deform.txt')
        with open(lmp_log_pwd, 'w') as output_file:  
            try:
                subprocess.run('python deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < deform.in > deform.log', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                # subprocess.run('python get_deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'semi模型力学性质计算完成，正在进行semi模型渗透性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型力学性质计算失败')  # 更新作业状态为失败
#semi模型渗透性质
        lmp_log_pwd = os.path.join(job_dir, 'Peameation.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:


                    subprocess.run('python cp_gcmc.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
        #提交gcmc作业
                    subprocess.run('sh gcmc_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型渗透性质--吸附性质计算完成，正在进行semi模型渗透性质--扩散计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型渗透性质--吸附性质计算失败')  # 更新作业状态为失败
    #复制last.data
            try:
                subprocess.run('python cp_msd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('sh msd_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'semi模型渗透性质--扩散性质计算完成，正在进行最后处理')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型渗透性质--扩散性质计算失败')  # 更新作业状态为失败
            # subprocess.run('python get_P_D_S.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)

            update_job_status(job_dir, '建模计算分析完成')  # 更新作业状态为完成
            socketio.emit('job_finished', {'job_dir': job_dir}, namespace='/job_state')  # 发送任务完成事件给客户端
        
    except subprocess.CalledProcessError:
        update_job_status(job_dir, '失败')  # 更新作业状态为失败

def process_coating_semi_job(job_dir, ncore, outfilename, filename, npoly, linkatom, order_nchain, disorder_nchain,lbox, step, annealing,
                rise_step, rise_equil_step, down_step, down_equil_step, anneal_tmp_start, anneal_tmp_down):
    try:
        max_attempts = 100  # 最大尝试次数
        attempt = 1
        while attempt <= max_attempts:
                
            try:
                #构建高分子lt文件
                subprocess.run('python3 semi_polymer_model.py', check=True, shell=True, timeout=60, cwd=job_dir)
                update_job_status(job_dir, '初始文件准备完毕,正在进行无定形高分子单链建模')  # 更新作业状态为完成
                break 
            # 命令成功执行，退出循环
            except subprocess.TimeoutExpired:
                if attempt < max_attempts:
                    # 命令执行失败，重新尝试
                    print(f'Command failed, retrying (attempt {attempt}/{max_attempts})')
                    update_job_status(job_dir, f'初始文件准备再次尝试，尝试次数：{attempt}/{max_attempts})')  # 更新作业状态为失败
                    attempt += 1
                    # 增加延迟等待后再次尝试
                    time.sleep(2)
                else:
                    # 达到最大尝试次数，抛出异常或执行其他操作
                    print('Command failed after maximum attempts')
                    raise
            except subprocess.CalledProcessError:
                update_job_status(job_dir, '初始文件准备失败')  # 更新作业状态为失败
        # 将输出重定向到文件
        log_pwd = os.path.join(job_dir, 'moltemplate_output.txt')
        try:
            with open(log_pwd, 'w') as output_file:
                #无定形高分子单链建模
                subprocess.run('moltemplate.sh tes' + str(npoly) + '.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, '无定形高分子单链建模完成,正在进行规则高分子整体建模')  # 更新作业状态为完成
        except subprocess.CalledProcessError:
            update_job_status(job_dir, '无定形高分子单链建模失败')  # 更新作业状态为失败
        log_pwd = os.path.join(job_dir, 'order_output.txt')
        with open(log_pwd, 'w') as output_file:
            try:

                #规则高分子整体建模
                subprocess.run('moltemplate.sh order_system.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)


                #subprocess.run('python write_system_lt.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                #根据规则高分子建模构建适合的无定形模型
                update_job_status(job_dir, '规则高分子建模完成,正在进行涂层建模')  # 更新作业状态为完成

                subprocess.run('python get_data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)

                subprocess.run('python write_semi_graphene.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('moltemplate.sh graphene_all.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('moltemplate.sh sio2_single_system_outside.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('python write_semi_graphene_packmol.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, '涂层建模完成,正在进行无定形高分子单链弛豫')  # 更新作业状态为完成
            except subprocess.CalledProcessError:
                update_job_status(job_dir, '规则高分子单链建模失败')  # 更新作业状态为失败
        lmp_log_pwd = os.path.join(job_dir, 'dis_equil.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:
                #无定形高分子单链弛豫
                subprocess.run('python dis_equil.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < dis_equil.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                
                update_job_status(job_dir, '无定形高分子单链弛豫完成，正在进行无定形高分子整体建模')  # 更新作业状态为完成
            except subprocess.CalledProcessError:
                update_job_status(job_dir, '无定形高分子单链弛豫失败')  # 更新作业状态为失败
        lmp_log_pwd = os.path.join(job_dir, 'packmol.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:
                
                    #无定形高分子整体建模
                subprocess.run('python dcd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)   
                subprocess.run('python data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)        
                subprocess.run('packmol < packmol.in  ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)        
                subprocess.run('moltemplate.sh -pdb system.pdb system.lt ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)          
                update_job_status(job_dir, '无定形高分子整体建模完成，正在进行无定形高分子整体弛豫')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, '无定形高分子整体建模失败')  # 更新作业状态为失败
# 无定形整体弛豫   
        lmp_log_pwd = os.path.join(job_dir, 'dis_sys_equil.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:
                
                subprocess.run('python dis_sys_equil.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < dis_sys_equil.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, '无定形高分子整体弛豫完成，正在进行semi模型整体建模')  # 更新作业状态为完成

                subprocess.run('python dis_dcd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)   
                subprocess.run('python dis_data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file) 
                subprocess.run('python order_data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file) 
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, '无定形高分子整体弛豫失败')  # 更新作业状态为失败
    #semi模型整体建模并弛豫
        lmp_log_pwd = os.path.join(job_dir, 'all_sys_model.txt')
        with open(lmp_log_pwd, 'w') as output_file:
                try:
                    subprocess.run('python sys_lt.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('python sys_packmol.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('packmol < sys_packmol.in  ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file) 
                    subprocess.run('moltemplate.sh -pdb all_sys.pdb all_sys.lt ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)     
                    update_job_status(job_dir, 'semi模型整体建模完成，正在进行semi模型整体退火')  # 更新作业状态为完成
                except subprocess.CalledProcessError or 'ERROR' in output_file:
                    update_job_status(job_dir, 'semi模型整体建模失败')  # 更新作业状态为失败
#semi模型整体退火            
        lmp_log_pwd = os.path.join(job_dir, 'all_sys_equil.txt')
        with open(lmp_log_pwd, 'w') as output_file:
                try:
                    subprocess.run('python all_sys.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < anneal.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型整体退火完成，正在进行semi模型Tg')  # 更新作业状态为完成
                except subprocess.CalledProcessError or 'ERROR' in output_file:
                    update_job_status(job_dir, 'semi模型整体退火失败')  # 更新作业状态为失败
                try:
                    subprocess.run('python get_Tg.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型Tg计算完成，正在进行semi模型FFV、PSD计算')  # 更新作业状态为完成
                except subprocess.CalledProcessError or 'ERROR' in output_file:
                    update_job_status(job_dir, 'semi模型Tg计算失败')  # 更新作业状态为失败
#semi模型孔径分布、孔隙率
        lmp_log_pwd = os.path.join(job_dir, 'FFV-PSD.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:

                    subprocess.run('python chat_data2cif.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -psd 0  100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -volpo  0 100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    # subprocess.run('python get_FFV_PSD.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型FFV、PSD计算完成，正在进行semi模型力学性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型FFV、PSD计算建模失败')  # 更新作业状态为失败
#semi模型力学性质
        lmp_log_pwd = os.path.join(job_dir, 'deform.txt')
        with open(lmp_log_pwd, 'w') as output_file:  
            try:
                subprocess.run('python deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < deform.in > deform.log', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                # subprocess.run('python get_deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'semi模型力学性质计算完成，正在进行semi模型渗透性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型力学性质计算失败')  # 更新作业状态为失败
#semi模型渗透性质
        lmp_log_pwd = os.path.join(job_dir, 'Peameation.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:


                    subprocess.run('python cp_gcmc.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
        #提交gcmc作业
                    subprocess.run('sh gcmc_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型渗透性质--吸附性质计算完成，正在进行semi模型渗透性质--扩散计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型渗透性质--吸附性质计算失败')  # 更新作业状态为失败
    #复制last.data
            try:
                subprocess.run('python cp_msd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('sh msd_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'semi模型渗透性质--扩散性质计算完成，正在进行最后处理')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型渗透性质--扩散性质计算失败')  # 更新作业状态为失败
            # subprocess.run('python get_P_D_S.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)

        update_job_status(job_dir, '建模计算分析完成')  # 更新作业状态为完成
        socketio.emit('job_finished', {'job_dir': job_dir}, namespace='/job_state')  # 发送任务完成事件给客户端
        
    except subprocess.CalledProcessError:
        update_job_status(job_dir, '失败')  # 更新作业状态为失败

def process_simple_job(job_dir, ncore, outfilename, filename, npoly, linkatom, nchain, lbox, step, annealing,
                rise_step, rise_equil_step, down_step, down_equil_step, anneal_tmp_start, anneal_tmp_down):
    try:
        max_attempts = 100  # 最大尝试次数
        attempt = 1

        while attempt <= max_attempts:
            try:
                subprocess.run('python simple_polymer_model.py', check=True, shell=True, timeout=10, cwd=job_dir)
                # 命令成功执行，退出循环
                break
            except subprocess.TimeoutExpired:
                if attempt < max_attempts:
                    # 命令执行失败，重新尝试
                    print(f'Command failed, retrying (attempt {attempt}/{max_attempts})')
                    attempt += 1
                    # 增加延迟等待后再次尝试
                    time.sleep(2)
                else:
                    # 达到最大尝试次数，抛出异常或执行其他操作
                    print('Command failed after maximum attempts')
                    raise

        # 将输出重定向到文件
        log_pwd = os.path.join(job_dir, 'moltemplate_output.txt')
        with open(log_pwd, 'w') as output_file:
            subprocess.run('moltemplate.sh tes' + str(npoly) + '.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            update_job_status(job_dir, 'disorder单链模型建模完成，正在进行disorder单链弛豫')  # 更新作业状态为完成

        log_pwd = os.path.join(job_dir, 'order_output.txt')
        with open(log_pwd, 'w') as output_file:
            subprocess.run('python write_pure_packmol.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
        print('Job', job_dir, 'has been modeled')

        lmp_log_pwd = os.path.join(job_dir, 'dis_equil.log')
        with open(lmp_log_pwd, 'w') as output_file:
            subprocess.run('python dis_equil.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < dis_equil.in', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            update_job_status(job_dir, 'disorder单链弛豫完成，正在进行disorder整体建模')  # 更新作业状态为完成

        lmp_log_pwd = os.path.join(job_dir, 'packmol.log')
        with open(lmp_log_pwd, 'w') as output_file:
            subprocess.run('python dcd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)   
            subprocess.run('python data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)        
            subprocess.run('packmol < packmol.in > packmol.log ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)        
            subprocess.run('moltemplate.sh -pdb system.pdb system.lt ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)     
            update_job_status(job_dir, 'disorder模型整体建模完成，正在进行disorder模型退火计算')  # 更新作业状态为完成


#模型整体退火            
        lmp_log_pwd = os.path.join(job_dir, 'anneal.log')
        with open(lmp_log_pwd, 'w') as output_file:
            subprocess.run('python anneal.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)

#anneal的初步弛豫过程提前
            subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < anneal.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
#退火后的模型构建石墨烯pdb文件
            subprocess.run('python write_simple_graphene.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            subprocess.run('moltemplate.sh graphene_all.lt ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)     
            subprocess.run('python write_simple_graphene_packmol.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            subprocess.run('packmol < simple_graphene_packmol.in > simple_graphene_packmol.log', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
#构建石墨烯data文件simple_graphene.lt未构建
            subprocess.run('moltemplate.sh -pdb simple_graphene.pdb simple_graphene.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)

            subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < anneal.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)



            subprocess.run('python get_Tg.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
            update_job_status(job_dir, 'disorder模型力学退火完成，正在进行disorder模型FFV、PSD计算')  # 更新作业状态为完成

#disorder模型孔径分布、孔隙率
        lmp_log_pwd = os.path.join(job_dir, 'FFV-PSD.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:

                    subprocess.run('python chat_data2cif.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -psd 0  100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -volpo  0 100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    # subprocess.run('python get_FFV_PSD.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'disorder模型FFV、PSD计算完成，正在进行disorder模型力学性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'disorder模型FFV、PSD计算建模失败')  # 更新作业状态为失败
#disorder模型力学性质
        lmp_log_pwd = os.path.join(job_dir, 'deform.txt')
        with open(lmp_log_pwd, 'w') as output_file:  
            try:
                subprocess.run('python deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < deform.in > deform.log', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                # subprocess.run('python get_deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'disorder模型力学性质计算完成，正在进行disorder模型渗透性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'disorder模型力学性质计算失败')  # 更新作业状态为失败
#disorder模型渗透性质
        lmp_log_pwd = os.path.join(job_dir, 'Peameation.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:


                    subprocess.run('python cp_gcmc.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
        #提交gcmc作业
                    subprocess.run('sh gcmc_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'disorder模型渗透性质--吸附性质计算完成，正在进行disorder模型渗透性质--扩散计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'disorder模型渗透性质--吸附性质计算失败')  # 更新作业状态为失败
    #复制last.data
            try:
                subprocess.run('python cp_msd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('sh msd_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'disorder模型渗透性质--扩散性质计算完成，正在进行最后处理')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'disorder模型渗透性质--扩散性质计算失败')  # 更新作业状态为失败
            # subprocess.run('python get_P_D_S.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)

        update_job_status(job_dir, '完成')  # 更新作业状态为完成
        socketio.emit('job_finished', {'job_dir': job_dir}, namespace='/job_state')  # 发送任务完成事件给客户端
        
    except subprocess.CalledProcessError:
        update_job_status(job_dir, '失败')  # 更新作业状态为失败

def process_coating_simple_job(job_dir, ncore, outfilename, filename, npoly, linkatom, nchain,lbox, step, annealing,
                rise_step, rise_equil_step, down_step, down_equil_step, anneal_tmp_start, anneal_tmp_down):
    try:
        max_attempts = 100  # 最大尝试次数
        attempt = 1
        while attempt <= max_attempts:
                
            try:
                #构建高分子lt文件
                subprocess.run('python3 simple_polymer_model.py', check=True, shell=True, timeout=60, cwd=job_dir)
                update_job_status(job_dir, '初始文件准备完毕,正在进行无定形高分子单链建模')  # 更新作业状态为完成
                break 
            # 命令成功执行，退出循环
            except subprocess.TimeoutExpired:
                if attempt < max_attempts:
                    # 命令执行失败，重新尝试
                    print(f'Command failed, retrying (attempt {attempt}/{max_attempts})')
                    update_job_status(job_dir, f'初始文件准备再次尝试，尝试次数：{attempt}/{max_attempts})')  # 更新作业状态为失败
                    attempt += 1
                    # 增加延迟等待后再次尝试
                    time.sleep(2)
                else:
                    # 达到最大尝试次数，抛出异常或执行其他操作
                    print('Command failed after maximum attempts')
                    raise
            except subprocess.CalledProcessError:
                update_job_status(job_dir, '初始文件准备失败')  # 更新作业状态为失败
        # 将输出重定向到文件
        log_pwd = os.path.join(job_dir, 'moltemplate_output.txt')
        try:
            with open(log_pwd, 'w') as output_file:
                #无定形高分子单链建模
                subprocess.run('moltemplate.sh tes' + str(npoly) + '.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, '无定形高分子单链建模完成,正在进行规则高分子整体建模')  # 更新作业状态为完成
        except subprocess.CalledProcessError:
            update_job_status(job_dir, '无定形高分子单链建模失败')  # 更新作业状态为失败
        log_pwd = os.path.join(job_dir, 'order_output.txt')
        with open(log_pwd, 'w') as output_file:
            try:

                #涂层建模
                subprocess.run('python write_semi_graphene.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('moltemplate.sh graphene_all.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('moltemplate.sh sio2_single_system_outside.lt', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                #弛豫单链
                #根据涂层构建适合的无定形模型


                #根据规则高分子建模构建适合的无定形模型
                update_job_status(job_dir, '规则高分子建模完成,正在进行涂层建模')  # 更新作业状态为完成

                subprocess.run('python get_data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)


                subprocess.run('python write_semi_graphene_packmol.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, '涂层建模完成,正在进行无定形高分子单链弛豫')  # 更新作业状态为完成
            except subprocess.CalledProcessError:
                update_job_status(job_dir, '规则高分子单链建模失败')  # 更新作业状态为失败
        lmp_log_pwd = os.path.join(job_dir, 'dis_equil.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:
                #无定形高分子单链弛豫
                subprocess.run('python dis_equil.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < dis_equil.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                
                update_job_status(job_dir, '无定形高分子单链弛豫完成，正在进行无定形高分子整体建模')  # 更新作业状态为完成
            except subprocess.CalledProcessError:
                update_job_status(job_dir, '无定形高分子单链弛豫失败')  # 更新作业状态为失败
        lmp_log_pwd = os.path.join(job_dir, 'packmol.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:
                
                    #无定形高分子整体建模
                subprocess.run('python dcd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)   
                subprocess.run('python data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)        
                subprocess.run('packmol < packmol.in  ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)        
                subprocess.run('moltemplate.sh -pdb system.pdb system.lt ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)          
                update_job_status(job_dir, '无定形高分子整体建模完成，正在进行无定形高分子整体弛豫')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, '无定形高分子整体建模失败')  # 更新作业状态为失败
# 无定形整体弛豫   
        lmp_log_pwd = os.path.join(job_dir, 'dis_sys_equil.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:
                
                subprocess.run('python dis_sys_equil.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < dis_sys_equil.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, '无定形高分子整体弛豫完成，正在进行semi模型整体建模')  # 更新作业状态为完成

                subprocess.run('python dis_dcd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)   
                subprocess.run('python dis_data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file) 
                subprocess.run('python order_data.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file) 
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, '无定形高分子整体弛豫失败')  # 更新作业状态为失败
    #semi模型整体建模并弛豫
        lmp_log_pwd = os.path.join(job_dir, 'all_sys_model.txt')
        with open(lmp_log_pwd, 'w') as output_file:
                try:
                    subprocess.run('python sys_lt.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('python sys_packmol.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('packmol < sys_packmol.in  ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file) 
                    subprocess.run('moltemplate.sh -pdb all_sys.pdb all_sys.lt ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)     
                    update_job_status(job_dir, 'semi模型整体建模完成，正在进行semi模型整体退火')  # 更新作业状态为完成
                except subprocess.CalledProcessError or 'ERROR' in output_file:
                    update_job_status(job_dir, 'semi模型整体建模失败')  # 更新作业状态为失败
#semi模型整体退火            
        lmp_log_pwd = os.path.join(job_dir, 'all_sys_equil.txt')
        with open(lmp_log_pwd, 'w') as output_file:
                try:
                    subprocess.run('python all_sys.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < anneal.in ', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型整体退火完成，正在进行semi模型Tg')  # 更新作业状态为完成
                except subprocess.CalledProcessError or 'ERROR' in output_file:
                    update_job_status(job_dir, 'semi模型整体退火失败')  # 更新作业状态为失败
                try:
                    subprocess.run('python get_Tg.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型Tg计算完成，正在进行semi模型FFV、PSD计算')  # 更新作业状态为完成
                except subprocess.CalledProcessError or 'ERROR' in output_file:
                    update_job_status(job_dir, 'semi模型Tg计算失败')  # 更新作业状态为失败
#semi模型孔径分布、孔隙率
        lmp_log_pwd = os.path.join(job_dir, 'FFV-PSD.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:

                    subprocess.run('python chat_data2cif.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -psd 0  100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    subprocess.run('network -volpo  0 100 100 final_300K.cif', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    # subprocess.run('python get_FFV_PSD.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型FFV、PSD计算完成，正在进行semi模型力学性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型FFV、PSD计算建模失败')  # 更新作业状态为失败
#semi模型力学性质
        lmp_log_pwd = os.path.join(job_dir, 'deform.txt')
        with open(lmp_log_pwd, 'w') as output_file:  
            try:
                subprocess.run('python deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('mpirun -np ' + str(ncore) + ' lmp_mpi < deform.in > deform.log', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                # subprocess.run('python get_deform.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'semi模型力学性质计算完成，正在进行semi模型渗透性质计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型力学性质计算失败')  # 更新作业状态为失败
#semi模型渗透性质
        lmp_log_pwd = os.path.join(job_dir, 'Peameation.txt')
        with open(lmp_log_pwd, 'w') as output_file:
            try:


                    subprocess.run('python cp_gcmc.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
        #提交gcmc作业
                    subprocess.run('sh gcmc_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                    update_job_status(job_dir, 'semi模型渗透性质--吸附性质计算完成，正在进行semi模型渗透性质--扩散计算')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型渗透性质--吸附性质计算失败')  # 更新作业状态为失败
    #复制last.data
            try:
                subprocess.run('python cp_msd.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                subprocess.run('sh msd_jobs.sh', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)
                update_job_status(job_dir, 'semi模型渗透性质--扩散性质计算完成，正在进行最后处理')  # 更新作业状态为完成
            except subprocess.CalledProcessError or 'ERROR' in output_file:
                update_job_status(job_dir, 'semi模型渗透性质--扩散性质计算失败')  # 更新作业状态为失败
            # subprocess.run('python get_P_D_S.py', check=True, shell=True, cwd=job_dir, stdout=output_file, stderr=output_file)

        update_job_status(job_dir, '建模计算分析完成')  # 更新作业状态为完成
        socketio.emit('job_finished', {'job_dir': job_dir}, namespace='/job_state')  # 发送任务完成事件给客户端
        
    except subprocess.CalledProcessError:
        update_job_status(job_dir, '失败')  # 更新作业状态为失败

@app.route('/tasks/simple', methods=['GET', 'POST'])
def simple():
    if request.method == 'POST':
        # 获取表单数据
        ncore = int(request.form['ncore'])
        outfilename = request.form['outfilename']
        filename = request.form['filename']
        npoly = request.form['npoly']
        linkatom = request.form['linkatom']
        nchain = int(request.form['nchain'])
        lbox = request.form['lbox']
        step = request.form['step']
        annealing = request.form['annealing']
        rise_step = int(request.form['rise_step'])
        rise_equil_step = int(request.form['rise_equil_step'])
        down_step = int(request.form['down_step'])
        down_equil_step = int(request.form['down_equil_step'])
        anneal_tmp_start = int(request.form['anneal_tmp_start'])
        anneal_tmp_down = int(request.form['anneal_tmp_down'])
        how_many_models = int(request.form['how many models'])
        current_dir = os.getcwd()
        threads = []

        for i in range(1, how_many_models+1):
            job_dir = os.path.join(current_dir, 'disorder-job' + str(i))
            src_dir = os.getcwd()+'/original_package'

            if not os.path.exists(job_dir):
                command = f'cp -r {src_dir}/* {job_dir}'
                os.makedirs(job_dir)

            else:
               print(f'Job directory {job_dir} already exists.')                
            command = f'cp -r {src_dir}/* {job_dir}'
            subprocess.run(command, check=True, shell=True, cwd=job_dir)
            inp_pwd = os.path.join(job_dir, 'in.inp')
            with open(inp_pwd, 'w') as f:
                f.write(f"ncore= {ncore}\n")
                f.write(f"outfilename= {outfilename}\n")
                f.write(f"filename= {filename}\n")
                f.write(f"npoly= {npoly}\n")
                f.write(f"linkatom= {linkatom}\n")
                f.write(f"nchain= {nchain}\n")
                f.write(f"lbox= {lbox}\n")
                f.write(f"step= {step}\n")
                f.write(f"annealing= {annealing}\n")
                f.write(f"rise_step= {rise_step}\n")
                f.write(f"rise_equil_step= {rise_equil_step}\n")
                f.write(f"down_step= {down_step}\n")
                f.write(f"down_equil_step= {down_equil_step}\n")
                f.write(f"anneal_tmp_start= {anneal_tmp_start}\n")
                f.write(f"anneal_tmp_down= {anneal_tmp_down}\n")
            all_poly=0
            if len(npoly)>1:
                for poly in npoly:
                    if poly != ' ':
                        all_poly+=int(poly)
                all_poly+=2    
                npoly=all_poly
            t = threading.Thread(target=process_job, args=(job_dir, ncore, outfilename, filename, npoly, linkatom,
                                                            nchain, lbox, step, annealing, rise_step,
                                                            rise_equil_step, down_step, down_equil_step,
                                                            anneal_tmp_start, anneal_tmp_down))
            t.start()
            threads.append(t)

            # 添加作业信息到全局变量
            job_info = {
                'job_dir': job_dir,
                'status': '运行中'
            }
            jobs.append(job_info)
            socketio.emit('new_job', job_info, namespace='/job_state')  # 发送新作业信息给客户端

        # 等待所有线程完成
        for t in threads:
            t.join()

        return redirect(url_for('job_state'))

    return render_template('simple.html')

@app.route('/tasks/crystal', methods=['GET', 'POST'])
def crystal():
    if request.method == 'POST':
        # 获取表单数据
        ncore = int(request.form['ncore'])
        outfilename = request.form['outfilename']
        filename = request.form['filename']
        npoly = request.form['npoly']
        linkatom = request.form['linkatom']
        nchain = int(request.form['nchain'])
        lbox = request.form['lbox']
        step = request.form['step']
        annealing = request.form['annealing']
        rise_step = int(request.form['rise_step'])
        rise_equil_step = int(request.form['rise_equil_step'])
        down_step = int(request.form['down_step'])
        down_equil_step = int(request.form['down_equil_step'])
        anneal_tmp_start = int(request.form['anneal_tmp_start'])
        anneal_tmp_down = int(request.form['anneal_tmp_down'])
        how_many_models = int(request.form['how many models'])
        current_dir = os.getcwd()
        threads = []

        for i in range(1, how_many_models+1):
            job_dir = os.path.join(current_dir, 'order-job' + str(i))
            src_dir = os.getcwd()+'/original_package'

            if not os.path.exists(job_dir):
                command = f'cp -r {src_dir}/* {job_dir}'
                os.makedirs(job_dir)
                subprocess.run(command, check=True, shell=True, cwd=job_dir)
                inp_pwd = os.path.join(job_dir, 'in.inp')
                with open(inp_pwd, 'w') as f:
                    f.write(f"ncore= {ncore}\n")
                    f.write(f"outfilename= {outfilename}\n")
                    f.write(f"filename= {filename}\n")
                    f.write(f"npoly= {npoly}\n")
                    f.write(f"linkatom= {linkatom}\n")
                    f.write(f"nchain= {nchain}\n")
                    f.write(f"lbox= {lbox}\n")
                    f.write(f"step= {step}\n")
                    f.write(f"annealing= {annealing}\n")
                    f.write(f"rise_step= {rise_step}\n")
                    f.write(f"rise_equil_step= {rise_equil_step}\n")
                    f.write(f"down_step= {down_step}\n")
                    f.write(f"down_equil_step= {down_equil_step}\n")
                    f.write(f"anneal_tmp_start= {anneal_tmp_start}\n")
                    f.write(f"anneal_tmp_down= {anneal_tmp_down}\n")
            else:
               print(f'Job directory {job_dir} already exists.')

            t = threading.Thread(target=process_crystal_job, args=(job_dir, ncore, outfilename, filename, npoly, linkatom,
                                                            nchain, lbox, step, annealing, rise_step,
                                                            rise_equil_step, down_step, down_equil_step,
                                                            anneal_tmp_start, anneal_tmp_down))
            t.start()
            threads.append(t)

            # 添加作业信息到全局变量
            job_info = {
                'job_dir': job_dir,
                'status': '运行中'
            }
            jobs.append(job_info)
            socketio.emit('new_job', job_info, namespace='/job_state')  # 发送新作业信息给客户端

        # 等待所有线程完成
        for t in threads:
            t.join()

        return redirect(url_for('job_state'))


    return render_template('crystal.html')

@app.route('/tasks/semi', methods=['GET', 'POST'])
def semi():
    if request.method == 'POST':
        # 获取表单数据
        ncore = int(request.form['ncore'])
        outfilename = request.form['outfilename']
        filename = request.form['filename']
        npoly = request.form['npoly']
        linkatom = request.form['linkatom']
        order_nchain = int(request.form['order_nchain'])
        disorder_nchain = int(request.form['disorder_nchain'])
        lbox = request.form['lbox']
        step = request.form['step']
        annealing = request.form['annealing']
        rise_step = int(request.form['rise_step'])
        rise_equil_step = int(request.form['rise_equil_step'])
        down_step = int(request.form['down_step'])
        down_equil_step = int(request.form['down_equil_step'])
        anneal_tmp_start = int(request.form['anneal_tmp_start'])
        anneal_tmp_down = int(request.form['anneal_tmp_down'])
        how_many_models = int(request.form['how many models'])
        current_dir = os.getcwd()
        threads = []

        for i in range(1, how_many_models+1):
            job_dir = os.path.join(current_dir, 'semi-job' + str(i))
            src_dir = current_dir+'/original_package'


            if not os.path.exists(job_dir):
                command = f'cp -r {src_dir}/* {job_dir}'
                os.makedirs(job_dir)
                subprocess.run(command, check=True, shell=True, cwd=job_dir)

            else:
                print(f'Job directory {job_dir} already exists.')
                # command = f'cp   {src_dir}/cp_gcmc.py {job_dir}'
                # subprocess.run(command, check=True, shell=True, cwd=job_dir)
            inp_pwd = os.path.join(job_dir, 'in.inp')
            while 1:
                if os.path.exists(inp_pwd):
                    break
                with open(inp_pwd, 'w') as f:
                    f.write(f"ncore= {ncore}\n")
                    f.write(f"outfilename= {outfilename}\n")
                    f.write(f"filename= {filename}\n")
                    f.write(f"npoly= {npoly}\n")
                    f.write(f"linkatom= {linkatom}\n")
                    f.write(f"order_nchain= {order_nchain}\n")
                    f.write(f"disorder_nchain= {disorder_nchain}\n")
                    f.write(f"lbox= {lbox}\n")
                    f.write(f"step= {step}\n")
                    f.write(f"annealing= {annealing}\n")
                    f.write(f"rise_step= {rise_step}\n")
                    f.write(f"rise_equil_step= {rise_equil_step}\n")
                    f.write(f"down_step= {down_step}\n")
                    f.write(f"down_equil_step= {down_equil_step}\n")
                    f.write(f"anneal_tmp_start= {anneal_tmp_start}\n")
                    f.write(f"anneal_tmp_down= {anneal_tmp_down}\n")

            t = threading.Thread(target=process_semi_job, args=(job_dir, ncore, outfilename, filename, npoly, linkatom,
                                                            order_nchain,disorder_nchain, lbox, step, annealing, rise_step,
                                                            rise_equil_step, down_step, down_equil_step,
                                                            anneal_tmp_start, anneal_tmp_down))
            t.start()
            threads.append(t)

            # 添加作业信息到全局变量
            job_info = {
                'job_dir': job_dir,
                'status': '运行中'
            }
            jobs.append(job_info)
            socketio.emit('new_job', job_info, namespace='/job_state')  # 发送新作业信息给客户端

        # 等待所有线程完成
        for t in threads:
            t.join()

        return redirect(url_for('job_state'))

    return render_template('semi.html')

@app.route('/graphene_silicon', methods=['GET', 'POST'])
def graphene_silicon():
    return render_template('graphene_silicon.html')

@app.route('/coating_semi', methods=['GET', 'POST'])
def coating_semi():
    if request.method == 'POST':
    # 获取表单数据
        ncore = int(request.form['ncore'])
        outfilename = request.form['outfilename']
        filename = request.form['filename']
        npoly = request.form['npoly']
        linkatom = request.form['linkatom']
        graphene = int(request.form['graphene'])
        silicon = int(request.form['silicon'])
        order_nchain = int(request.form['order_nchain'])
        disorder_nchain = int(request.form['disorder_nchain'])
        lbox = request.form['lbox']
        step = request.form['step']
        annealing = request.form['annealing']
        rise_step = int(request.form['rise_step'])
        rise_equil_step = int(request.form['rise_equil_step'])
        down_step = int(request.form['down_step'])
        down_equil_step = int(request.form['down_equil_step'])
        anneal_tmp_start = int(request.form['anneal_tmp_start'])
        anneal_tmp_down = int(request.form['anneal_tmp_down'])
        how_many_models = int(request.form['how many models'])
        current_dir = os.getcwd()
        threads = []

        for i in range(1, how_many_models+1):
            job_dir = os.path.join(current_dir, 'semi-job' + str(i))
            src_dir = current_dir+'/original_package'


            if not os.path.exists(job_dir):
                command = f'cp -r {src_dir}/* {job_dir}'
                os.makedirs(job_dir)
                subprocess.run(command, check=True, shell=True, cwd=job_dir)

            else:
                print(f'Job directory {job_dir} already exists.')
                # command = f'cp   {src_dir}/cp_gcmc.py {job_dir}'
                # subprocess.run(command, check=True, shell=True, cwd=job_dir)
            inp_pwd = os.path.join(job_dir, 'in.inp')
            while 1:
                if os.path.exists(inp_pwd):
                    break
                with open(inp_pwd, 'w') as f:
                    f.write(f"ncore= {ncore}\n")
                    f.write(f"outfilename= {outfilename}\n")
                    f.write(f"filename= {filename}\n")
                    f.write(f"npoly= {npoly}\n")
                    f.write(f"linkatom= {linkatom}\n")
                    f.write(f"graphene= {graphene}\n")
                    f.write(f"silicon= {silicon}\n")
                    f.write(f"order_nchain= {order_nchain}\n")
                    f.write(f"disorder_nchain= {disorder_nchain}\n")
                    f.write(f"lbox= {lbox}\n")
                    f.write(f"step= {step}\n")
                    f.write(f"annealing= {annealing}\n")
                    f.write(f"rise_step= {rise_step}\n")
                    f.write(f"rise_equil_step= {rise_equil_step}\n")
                    f.write(f"down_step= {down_step}\n")
                    f.write(f"down_equil_step= {down_equil_step}\n")
                    f.write(f"anneal_tmp_start= {anneal_tmp_start}\n")
                    f.write(f"anneal_tmp_down= {anneal_tmp_down}\n")

            t = threading.Thread(target=process_coating_semi_job, args=(job_dir, ncore, outfilename, filename, npoly, linkatom,
                                                            order_nchain,disorder_nchain, lbox, step, annealing, rise_step,
                                                            rise_equil_step, down_step, down_equil_step,
                                                            anneal_tmp_start, anneal_tmp_down))
            t.start()
            threads.append(t)

            # 添加作业信息到全局变量
            job_info = {
                'job_dir': job_dir,
                'status': '运行中'
            }
            jobs.append(job_info)
            socketio.emit('new_job', job_info, namespace='/job_state')  # 发送新作业信息给客户端

        # 等待所有线程完成
        for t in threads:
            t.join()

        return redirect(url_for('job_state'))
    return render_template('coating_semi.html')

@app.route('/coating_simple', methods=['GET', 'POST'])
def coating_simple():
    if request.method == 'POST':
        # 获取表单数据
        ncore = int(request.form['ncore'])
        outfilename = request.form['outfilename']
        filename = request.form['filename']
        npoly = request.form['npoly']
        linkatom = request.form['linkatom']
        graphene = int(request.form['graphene'])
        silicon = int(request.form['silicon'])
        nchain = int(request.form['nchain'])
        lbox = request.form['lbox']
        step = request.form['step']
        annealing = request.form['annealing']
        rise_step = int(request.form['rise_step'])
        rise_equil_step = int(request.form['rise_equil_step'])
        down_step = int(request.form['down_step'])
        down_equil_step = int(request.form['down_equil_step'])
        anneal_tmp_start = int(request.form['anneal_tmp_start'])
        anneal_tmp_down = int(request.form['anneal_tmp_down'])
        how_many_models = int(request.form['how many models'])
        current_dir = os.getcwd()
        threads = []

        for i in range(1, how_many_models+1):
            job_dir = os.path.join(current_dir, 'disorder-job' + str(i))
            src_dir = os.getcwd()+'/original_package'

            if not os.path.exists(job_dir):
                command = f'cp -r {src_dir}/* {job_dir}'
                os.makedirs(job_dir)

            else:
               print(f'Job directory {job_dir} already exists.')                
            command = f'cp -r {src_dir}/* {job_dir}'
            subprocess.run(command, check=True, shell=True, cwd=job_dir)
            inp_pwd = os.path.join(job_dir, 'in.inp')
            with open(inp_pwd, 'w') as f:
                f.write(f"ncore= {ncore}\n")
                f.write(f"outfilename= {outfilename}\n")
                f.write(f"filename= {filename}\n")
                f.write(f"npoly= {npoly}\n")
                f.write(f"linkatom= {linkatom}\n")
                f.write(f"graphene= {graphene}\n")
                f.write(f"silicon= {silicon}\n")
                f.write(f"nchain= {nchain}\n")
                f.write(f"lbox= {lbox}\n")
                f.write(f"step= {step}\n")
                f.write(f"annealing= {annealing}\n")
                f.write(f"rise_step= {rise_step}\n")
                f.write(f"rise_equil_step= {rise_equil_step}\n")
                f.write(f"down_step= {down_step}\n")
                f.write(f"down_equil_step= {down_equil_step}\n")
                f.write(f"anneal_tmp_start= {anneal_tmp_start}\n")
                f.write(f"anneal_tmp_down= {anneal_tmp_down}\n")
            t = threading.Thread(target=process_coating_simple_job, args=(job_dir, ncore, outfilename, filename, npoly, linkatom,
                                                            nchain, lbox, step, annealing, rise_step,
                                                            rise_equil_step, down_step, down_equil_step,
                                                            anneal_tmp_start, anneal_tmp_down))
            t.start()
            threads.append(t)

            # 添加作业信息到全局变量
            job_info = {
                'job_dir': job_dir,
                'status': '运行中'
            }
            jobs.append(job_info)
            socketio.emit('new_job', job_info, namespace='/job_state')  # 发送新作业信息给客户端

        # 等待所有线程完成
        for t in threads:
            t.join()

        return redirect(url_for('job_state'))
    return render_template('coating_simple.html')

if __name__ == '__main__':
    socketio.run(app, debug=False, port=8888, host='0.0.0.0')
