from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import hashlib
import os
import pytz
from datetime import datetime

app = Flask(__name__, template_folder="E:/毕设/website/HTML", static_folder="E:/毕设/website/CJI")   # 路径还没搞好，还是会出现后端运行，但前端跳转不了网页


def get_db_connection():    # 用户信息数据库
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_ESP_connection():  # ESP01S发的传感器数据库
    conn = sqlite3.connect('databaseESP.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_Control_Web_connnection():
    conn = sqlite3.connect('databaseCon.db')
    conn.row_factory = sqlite3.Row
    return conn


# 初始化用户数据库
def init_db():
    conn = get_db_connection()
    c = conn.cursor()     # 游标
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,    
                  password TEXT NOT NULL)''')   # 上面面是对数据库的所存内容定义
    conn.commit()
    conn.close()


# 初始化温湿度数据库
def init_ESP():
    conn = get_ESP_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS esp
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                Temp TEXT NOT NULL,
                RH TEXT NOT NULL,
                time DATETIME DEFAULT CURRENT_TIMESTAMP)''')  # DEFAULT DATETIME('now', "localtime")
    conn.commit()  # 提交数据库的更改
    conn.close()   # 释放资源


# 初始化控制指令数据库
def init_Con():
    conn = get_Control_Web_connnection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Con
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                TH TEXT NOT NULL,
                TL TEXT NOT NULL,
                RH TEXT NOT NULL,
                RL TEXT NOT NULL)''')
    conn.commit()
    conn.close()


# 定义主路由，渲染登录页面
@app.route('/')
def home():
    return render_template('signin.html')  # 渲染 signin.html 页面作为首页


# 注册页面路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(request.form)
        username = request.form['username']
        password = request.form['password']
        # 对密码进行哈希处理
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return redirect(url_for('signin'))  # 跳转页面函数 ,统一资源定位符url,表明 Flask 的url_for() 函数没有成功生成对应的 URL，原因可能是您传入的参数不正确。具体问题出在 url_for('../website/HTML/signin.html')，因为 url_for() 是根据路由的端点名称（函数名）生成 URL，而不能直接传递文件路径。
    return render_template('registerpass.html')     # 回到之前的页面 之前网页老是与我的后端代码无法连接，一开始以为是网页的插件liver的script代码出了问题，查询大量资料，后面发现是调用这个函数render_template 的路径没给对


# 登录页面路由
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 对密码进行哈希处理
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = c.fetchone()
        if user:
            # return "登录成功！"
            return render_template('showdata.html')
        else:
            return "用户名或密码错误"
    return render_template('signin.html')     # 之前使用相对地址，会导致Flash无法准确找到其网页地址


# 修改密码
@app.route('/change', methods=['GET', 'POST'])
def change():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 对密码进行哈希处理
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # 连接数据库
        conn = get_db_connection()
        c = conn.cursor()
        # 验证用户
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()  # 查阅结果

        if user:
            c.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, username))
            conn.commit()   # 更新用户的数据
            conn.close()
            return render_template('signin.html')
        else:
            conn.close()
            return "不存在该账号"
    return render_template('changepass.html')


data_list = []   # 用于ESP01S的数据的计数


# 接收ESP01S的数据
@app.route('/receive', methods=['POST'])   # 此处还是用POST，因为简单的网页一般是GET指令
def receive():
    global data_list
    data = request.form.get('data')  # 获取ESP01S发送的数据中data的值
    print(request.form)   # 调试查看
    print(ord(data))      # 调试查看
    data_list.append(ord(data))    # 将获取的16进制转换为10进制并存储在数组中
    if len(data_list) == 2:
        # 获取本地时间
        bj_time_s = pytz.timezone('Asia/Shanghai')
        bj_time = datetime.now(bj_time_s).strftime('%Y-%m-%d %H:%M:%S')
        # 存放数据进ESPdb
        conn = get_ESP_connection()
        c = conn.cursor()
        c.execute('INSERT INTO esp (Temp,RH,time) VALUES (?, ?, ?)', (data_list[0], data_list[1], bj_time))
        conn.commit()
        conn.close()
        data_list.clear()    # 清空数组
        return jsonify({"message": "Two data entries saved successfully!"})  # 返回成功信息
    return jsonify({"message": "Data received, waiting for another entry..."})  # 等待更多数据

# 目前了解到的是，无法直接把数据发送给前端，需要前端向后端请求数据，故需要另外的一个路由。但怎么储存数据，并在下一个路由中把数据发送出去，怎么编写前端的网页代码和JS代码是一个难点


# 创建网页访问后端可以获得数据的路由
@app.route('/get_data', methods=['GET', 'POST'])
def get_data():
    e = get_ESP_connection()  # 打开数据库
    ec = e.cursor()
    ec.execute('SELECT * FROM esp')  # 获取ESP数据库数据
    data = ec.fetchall()    # 获取查询结果，格式为列表，每个元素为数据库的一行
    data = data[::-1]   # 把数据库里面的最新的数据放前面
    e.close()   # 关闭数据库连接
    return jsonify([dict(row) for row in data])


# 网页发送阈值数据，后端路由接收
data_send = []  # 用于临时存放阈值数据
# 这样只会在有数据的时候才刷新，另建一个数据库来存放这些指令吧


@app.route('/change_data', methods=['GET', 'POST'])
def change_data():
    global data_send
    if request.method == 'POST':
        data_send.append(int(request.form['TempH']))
        data_send.append(int(request.form['TempL']))
        data_send.append(int(request.form['RHH']))
        data_send.append(int(request.form['RHL']))
        print(data_send)
        # 存放指令进数据库
        conn = get_Control_Web_connnection()
        c = conn.cursor()
        c.execute('INSERT INTO Con (TH,TL,RH,RL) VALUES(?,?,?,?)', (data_send[0], data_send[1], data_send[2], data_send[3]))
        conn.commit()
        conn.close()
        # 清空列表数据
        data_send.clear()
        return render_template('showdata.html')
    return "发送数据失败"


# 由ESP01S来向后端获取数据
@app.route('/send_data', methods=['GET'])
def send_data():
    # 从数据库获取数据
    c = get_Control_Web_connnection()
    cc = c.cursor()
    cc.execute('SELECT * FROM Con ORDER BY id DESC LIMIT 1')  # 按降序排列数据库
    data = cc.fetchone()
    print(data)
    print(dict(data))
    return jsonify(dict(data))


if __name__ == '__main__':
    init_db()
    init_ESP()
    init_Con()
    print("Template folder:", app.template_folder)
    print("Database path:", os.path.abspath('Database/database.db'))
    print("DataESP path", os.path.abspath('Database/databaseESP.db'))
    app.run(debug=True, host='192.168.4.2', port=5500)    # 更改致一样的port地址, 为了连接ESP01S，更改了本地IP地址  , host='192.168.4.2'


