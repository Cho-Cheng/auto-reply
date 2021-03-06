'''
    主要思路:
        1. 点击图片按钮后选择图片发送
        2. 先将图片发送到服务端缓存文件夹,发送完成后发信息通知各个客户端
        3. 客户端收到后会从服务端的缓存文件夹中下载对应的图片并打印到聊天界面,
           同样是在接收后进行判断进行操作
    开始第3步: recv函数的表情判断中再增加一个判断,
               如果是表情图就贴表情, 如果是图片则先用print代替 
'''

import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText  # 导入多行文本框用到的包
import time
import os
from tkinter import filedialog
import requests

IP = ''
PORT = ''
user = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
online_users = []  # 在线用户列表
chat = '----------群聊----------'  # 聊天对象, 默认为群聊

## 登录窗口
root1 = tkinter.Tk()
root1.title('登录')
root1['height'] = 110
root1['width'] = 270
root1.resizable(0, 0)  # 限制窗口大小

IP1 = tkinter.StringVar()
IP1.set('127.0.0.1:50007')  # 默认显示的ip和端口
User = tkinter.StringVar()
User.set('')

# 服务器标签
labelIP = tkinter.Label(root1, text='服务器地址')
labelIP.place(x=30, y=10, width=80, height=20)

entryIP = tkinter.Entry(root1, width=80, textvariable=IP1)
entryIP.place(x=120, y=10, width=130, height=20)

# 用户名标签
labelUser = tkinter.Label(root1, text='用户名')
labelUser.place(x=30, y=40, width=80, height=20)

entryUser = tkinter.Entry(root1, width=80, textvariable=User)
entryUser.place(x=120, y=40, width=130, height=20)

# 登录按钮
def login(*args):
    global IP, PORT, user
    IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
    PORT = int(PORT)  # 端口号需要为int类型
    user = entryUser.get()
    root1.destroy()  # 关闭窗口
root1.bind('<Return>', login)  # 回车绑定登录功能

but = tkinter.Button(root1, text='登录', command=login)
but.place(x=100, y=70, width=70, height=30)

root1.mainloop()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

# try:Maybe on
if user:
    s.send(user.encode())  # 发送用户名
else:
    s.send('no'.encode())  # 没有输入用户名则标记no

# 如果没有用户名则将ip和端口号设置为用户名
addr = s.getsockname()  # 获取客户端ip和端口号
addr = addr[0] + ':' + str(addr[1])
if user == '':
    user = addr

## 聊天窗口
# 创建图形界面
root = tkinter.Tk()
root.title(user)  # 窗口命名为用户名
root['height'] = 390
root['width'] = 580
root.resizable(0, 0)  # 限制窗口大小

# 创建多行文本框
listbox = ScrolledText(root)
listbox.place(x=5, y=0, width=570, height=320)
# 文本框使用的字体颜色
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.insert(tkinter.END, '欢迎进入聊天室!', 'blue')

###### 表情功能代码部分
# 四个按钮, 使用全局变量, 方便创建和销毁
b1 = ''
b2 = ''
b3 = ''
b4 = ''
# 将图片打开存入变量中
p1 = tkinter.PhotoImage(file = './表情/捂脸.png')
p2 = tkinter.PhotoImage(file = './表情/奸笑.png')
p3 = tkinter.PhotoImage(file = './表情/皱眉.png')
p4 = tkinter.PhotoImage(file = './表情/机智.png')
# 用字典将标记与表情图片一一对应, 用于后面接收标记判断表情贴图
dic = {'aa**':p1, 'bb**':p2, 'cc**':p3, 'dd**':p4}
ee = 0  # 判断表情面板开关的标志
# 发送表情图标记的函数, 在按钮点击事件中调用
def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    global ee
    mes = exp + ':;' + user + ':;' + chat
    s.send(mes.encode())
    b1.destroy()
    b2.destroy()
    b3.destroy()
    b4.destroy()
    ee = 0
    
# 四个对应的函数
def bb1():
    mark('aa**')
def bb2():
    mark('bb**')
def bb3():
    mark('cc**')
def bb4():
    mark('dd**')
def express():
    global b1, b2, b3, b4, ee
    if ee == 0:
        ee = 1
        b1 = tkinter.Button(root, command=bb1, image=p1,
                            relief=tkinter.FLAT ,bd=0)
        b2 = tkinter.Button(root, command=bb2, image=p2,
                            relief=tkinter.FLAT ,bd=0)
        b3 = tkinter.Button(root, command=bb3, image=p3,
                            relief=tkinter.FLAT ,bd=0)
        b4 = tkinter.Button(root, command=bb4, image=p4,
                            relief=tkinter.FLAT ,bd=0)

        b1.place(x=5, y=248)
        b2.place(x=75, y=248)
        b3.place(x=145, y=248)
        b4.place(x=215, y=248)
    else:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()
    
# 创建表情按钮
eBut = tkinter.Button(root, text='表情', command=express)
eBut.place(x=5, y=320, width=60, height=30)

###### 图片功能代码部分
# 将图片上传到图片服务端的缓存文件夹中
def filePut(fileName):
    PORT3 = 50009
    ss = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    ss.connect((IP, PORT3))
    # 截取文件名
    name = fileName.split('/')[-1]
    message = 'put  ' + name
    ss.send(message.encode())
    time.sleep(0.1)
    print('开始上传文件!')
    with open(fileName, 'rb') as f:
        while True:
            a = f.read(1024)
            if not a:
                break
            ss.send(a)
        time.sleep(0.1)  # 延时确保文件发送完整
        ss.send('EOF'.encode())
        print('文件上传成功')
    ss.send('quit'.encode())
    time.sleep(0.1)
    # 上传成功后发一个信息给所有客户端
    mes = '``#' + name + ':;' + user + ':;' + chat
    s.send(mes.encode())


def picture():
    # 选择对话框
    fileName = tkinter.filedialog.askopenfilename(title='选择上传文件')
    # 如果有选择文件才继续执行
    if fileName:
        # 调用发送图片函数
        filePut(fileName)
    
# 创建发送图片按钮
pBut = tkinter.Button(root, text='图片', command=picture)
pBut.place(x=65, y=320, width=60, height=30)

def shot():
    pass
# 创建截屏按钮
sBut = tkinter.Button(root, text='截屏', command=shot)
sBut.place(x=125, y=320, width=60, height=30)

###### 文件功能代码部分
## 将在文件功能窗口用到的组件名都列出来, 方便重新打开时会对面板进行更新
list2 = ''  # 列表框
label = ''  # 显示路径的标签
upload = ''  # 上传按钮
close = ''  # 关闭按钮
def fileClient():
    PORT2 = 50008    # 聊天室的端口为50007
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.connect((IP, PORT2))

    # 修改root窗口大小显示文件管理的组件
    root['height'] = 390
    root['width'] = 760

    # 创建列表框
    list2 = tkinter.Listbox(root)
    list2.place(x=580, y=25, width=175, height=325)

    # 将接收到的目录文件列表打印出来(dir), 显示在列表框中, 在pwd函数中调用
    def recvList(enter, lu):
        s.send(enter.encode())
        data = s.recv(4096)  
        data = json.loads(data.decode())
        list2.delete(0, tkinter.END)  # 清空列表框
        lu = lu.split('\\')
        if len(lu) != 1:
            list2.insert(tkinter.END, ' 返回上一级目录')
            list2.itemconfig(0, fg='green')
        for i in range(len(data)):
            list2.insert(tkinter.END, (' '+data[i]))
            if not '.' in data[i]:
                list2.itemconfig(tkinter.END, fg='orange')
            else:
                list2.itemconfig(tkinter.END, fg='blue')

    # 创建标签显示服务端工作目录
    def lab():
        global label
        data = s.recv(1024)  # 接收目录
        lu = data.decode()
        try:
            label.destroy()
            label = tkinter.Label(root, text=lu)
            label.place(x=580, y=0, )
        except:
            label = tkinter.Label(root, text=lu)
            label.place(x=580, y=0, )
        recvList('dir', lu)

    # 进入指定目录(cd)
    def cd(message):
        s.send(message.encode())

    # 刚连接上服务端时进行一次面板刷新    
    cd('cd same')
    lab()

    # 接收下载文件(get)
    def get(message):
        name = message.split()
        name = name[1]  # 获取命令的第二个参数(文件名)
        # 选择对话框, 选择文件的保存路径
        fileName = tkinter.filedialog.asksaveasfilename(title='保存文件到',
                                            initialfile=name)
        # 如果文件名非空才进行下载
        if fileName:
            s.send(message.encode())
            with open(fileName, 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if data == 'EOF'.encode():
                        tkinter.messagebox.showinfo(title='提示',
                                                    message='下载成功!')
                        break
                    f.write(data)

    # 创建用于绑定在列表框上的函数
    def run(*args):
        indexs = list2.curselection()
        index = indexs[0]
        content = list2.get(index)
        # 如果有一个 . 则为文件
        if '.' in content:
            content = 'get' + content
            get(content)
            cd('cd same')
        elif content == ' 返回上一级目录':
            content = 'cd ..'
            cd(content)
        else:
            content = 'cd ' + content
            cd(content)
        lab()  # 刷新显示页面
        
    # 在列表框上设置绑定事件
    list2.bind('<ButtonRelease-1>', run)

    # 上传客户端所在文件夹中指定的文件到服务端, 在函数中获取文件名, 不用传参数
    def put():
        # 选择对话框
        fileName = tkinter.filedialog.askopenfilename(title='选择上传文件')
        # 如果有选择文件才继续执行
        if fileName:
            name = fileName.split('/')[-1]
            message = 'put ' + name
            s.send(message.encode())
            with open(fileName, 'rb') as f:
                while True:
                    a = f.read(1024)
                    if not a:
                        break
                    s.send(a)
                time.sleep(0.1)  # 延时确保文件发送完整
                s.send('EOF'.encode())
                tkinter.messagebox.showinfo(title='提示',
                                            message='上传成功!')
        cd('cd same')
        lab()  # 上传成功后刷新显示页面

    # 创建上传按钮, 并绑定上传文件功能
    upload = tkinter.Button(root, text='上传文件', command=put)
    upload.place(x=600, y=353, height=30, width=80)

    # 关闭文件管理器, 待完善
    def closeFile():
        root['height'] = 390
        root['width'] = 580
        # 关闭连接
        s.send('quit'.encode())
        s.close()

    # 创建关闭按钮
    close = tkinter.Button(root, text='关闭', command=closeFile)
    close.place(x=685, y=353, height=30, width=70) 

def file():
    fileClient()
    
# 创建文件按钮
fBut = tkinter.Button(root, text='文件', command=file)
fBut.place(x=185, y=320, width=60, height=30)

# 创建多行文本框, 显示在线用户
listbox1 = tkinter.Listbox(root)  
listbox1.place(x=445, y=0, width=130, height=320)

def users():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=130, height=320)
        ii = 0
    else:
        listbox1.place_forget()  # 隐藏控件
        ii = 1
    
# 查看在线用户按钮
button1 = tkinter.Button(root, text='在线用户', command=users)
button1.place(x=505, y=320, width=70, height=30)

# 创建输入文本框和关联变量
a = tkinter.StringVar()
a.set('')
entry = tkinter.Entry(root, width=120, textvariable=a)
entry.place(x=5, y=348, width=570, height=40)

'''  '''
def call_robot(url, apikey, msg):
    data = {  # 这个是在帮助手册上直接复制过来的，"url"=="https://www.kancloud.cn/turing/www-tuling123-com/718227"
        # """与reqType在同一级的参数有：{
        # reqType : 输入类型
        # perception : 输入信息
        # userInfo : 用户参数"""
        "reqType": 0,
        # '''# reqType为int类型，可以为空，
        # 输入类型:{
        # 0:文本(默认)
        # 1:图片
        # 2:音频
        # }'''
        "perception": {  # perception为用户输入信息，不允许为空
            # """
            # perception参数中的参数有：{
            # inputText : 文本信息
            # inputImage : 图片信息
            # inputMedia : 音频信息
            # selfInfo : 客户端属性
            # }
            # 注意：输入参数必须包含inputText或inputImage或inputMedia，可以是其中的任何一个\n            # 也可以是全部！
            # """
            # 用户输入文文信息
            "inputText": {  # inputText文本信息
                "text": msg
            },
            # 用户输入图片url
            "inputImage": {  # 图片信息，后跟参数信息为url地址，string类型
                "url": "https://cn.bing.com/images/"
            },
            # 用户输入音频地址信息
            "inputMedia": {  # 音频信息，后跟参数信息为url地址，string类型
                "url": "https://www.1ting.com/"
            },
            # 客户端属性信息
            "selfInfo": {  # location 为selfInfo的参数信息，
                "location": {  # 地理位置信息
                    "city": "杭州",  # 所在城市，不允许为空
                    "province": "浙江省",  # 所在省份，允许为空
                    "street": "灵隐街道"  # 所在街道，允许为空
                }
            },
        },
        "userInfo": {  # userInfo用户参数，不允许为空
            # """
            # "userInfo包含的参数":{
            # "apiKey" : {
            #     "类型" : "String",
            #     "是否必须" : "Y ",
            #     "取值范围" : "32位",
            #     "说明" : "机器人标识"
            #     }
            # "userId" : {
            #     "类型" : "String",
            #     "是否必须" : "Y ",
            #     "取值范围" : "长度小于等于32位",
            #     "说明" : "用户唯一标识"
            #     }
            # "gropId" : {
            #     "类型" : "String",
            #     "是否必须" : "N ",
            #     "取值范围" : "长度小于等于64位",
            #     "说明" : "群聊唯一标识"
            #     }
            # "userIdName" : {
            #     "类型" : "String",
            #     "是否必须" : "N ",
            #     "取值范围" : "长度小于等于64位",
            #     "说明" : "群内用户昵称"
            #     }
            # }
            # """
            "apiKey": "ee19328107fa41e987a42a064a68d0da",  # 你注册的apikey,机器人标识,32位
            "userId": "Brandon"  # 随便填，用户的唯一标识，长度小于等于32位
        }
    }
    headers = {'content-type': 'application/json'}  # 必须是json
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return r.json()






def send(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    online_users.append('----------群聊----------')  
    # try:begin
    online_users.append('Robot')
    
    # try:end
    if chat not in online_users:
        tkinter.messagebox.showerror('发送失败', message = '没有聊天对象!')
        return
    # try:begin
    if chat == 'Robot':
        print('Robot')
        # apikey = 'ee19328107fa41e987a42a064a68d0da'
        # url = 'http://openapi.tuling123.com/openapi/api/v2'
        # msg = entry.get()
        # print('msg = ',msg)
        # reply = call_robot(url, apikey, msg)
        # reply_txt = '\nRobot_Cheng:' + reply['results'][0]['values']['text']
        # print('reply = ',reply)
        # listbox.insert(tkinter.END, reply_txt, 'red')
    # try:end
    if chat == user:
        tkinter.messagebox.showerror('发送失败', message = '不能私聊自己!')
        return
    mes = entry.get() + ':;' + user + ':;' + chat  # 添加聊天对象标记
    s.send(mes.encode())
    a.set('')  # 发送后清空文本框
    
# 创建发送按钮
button = tkinter.Button(root, text='发送', command=send)
button.place(x=515, y=353, width=60, height=30)
root.bind('<Return>', send)  # 绑定回车发送信息



def private(*args):
    global chat
    # 获取点击的索引然后得到内容(用户名)
    indexs = listbox1.curselection()
    index = indexs[0]
    chat = listbox1.get(index)
    # 修改客户端名称
    if chat == '----------群聊----------':
        root.title(user)
        return       
    ti = user + '  -->  ' + chat
    root.title(ti)
    # print(socket.gethostbyname(socket.getfqdn(socket.gethostname())))

# 在显示用户列表框上设置绑定事件
listbox1.bind('<ButtonRelease-1>', private)
# 用于时刻接收服务端发送的信息并打印,
def recv():
    global online_users
    while True:
        data = s.recv(1024)
        data = data.decode()
        # 没有捕获到异常则表示接收到的是在线用户列表
        try:
            data = json.loads(data)
            online_users = data
            listbox1.delete(0, tkinter.END)  # 清空列表框
            number = ('     在线人数: ' + str(len(data)) + ' 人')
            listbox1.insert(tkinter.END, number)
            listbox1.itemconfig(tkinter.END, fg='green', bg="#f0f0ff")
            listbox1.insert(tkinter.END, '----------群聊----------')
            listbox1.insert(tkinter.END,'Robot')
            listbox1.itemconfig(tkinter.END, fg='green')
            for i in range(len(data)):
                listbox1.insert(tkinter.END, (data[i]))
                listbox1.itemconfig(tkinter.END, fg='green')
        except:
            data = data.split(':;')
            print('data = ',data)
            print('len(data) = ',len(data))
            if len(data) == 4:
                auto_reply = data[3]
                print('auto_reply = ',auto_reply)
                print('type(auto_reply) = ',type(auto_reply))
            data1 = data[0].strip()  # 消息
            print('data1 = ',data1)
            data2 = data[1]  # 发送信息的用户名
            print('data2 = ',data2)
            data3 = data[2]  # 聊天对象
            print('data3 = ',data3)
            markk = data1.split('：')[1]
            # 判断是不是图片
            pic = markk.split('#')
            # 判断是不是表情
            # 如果字典里有则贴图
            if (markk in dic) or pic[0] == '``':
                data4 = '\n' + data2 + '：'  # 例:名字-> \n名字：
                if data3 == '----------群聊----------':
                    if data2 == user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, data4, 'blue')
                    else:
                        listbox.insert(tkinter.END, data4, 'green')  # END将信息加在最后一行
                elif data2 == user or data3 == user:  # 显示私聊
                    listbox.insert(tkinter.END, data4, 'red')  # END将信息加在最后一行 
                if pic[0] == '``':
                    print('图片')
                else:
                    listbox.image_create(tkinter.END, image=dic[markk])
            else:
                data_msg = data1.split('：')[1]
                print('msg =',data_msg)
                data1 = '\n' + data1
                if data3 == '----------群聊----------':
                    if data2 == user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, data1, 'blue')
                    else:
                        print('here')
                        listbox.insert(tkinter.END, data1, 'green')  # END将信息加在最后一行
                    if len(data) == 4:
                        listbox.insert(tkinter.END, '\n' + data[3], 'red')
                elif data3 == 'Robot':
                    print('Here:Robot')
                    apikey = 'ee19328107fa41e987a42a064a68d0da'
                    url = 'http://openapi.tuling123.com/openapi/api/v2'
                    # msg = entry.get()
                    print('msg = ',data1)
                    listbox.insert(tkinter.END, data1, 'blue')
                    reply = call_robot(url, apikey, data_msg)
                    reply_txt = '\nRobot_Cheng:' + reply['results'][0]['values']['text']
                    # print('reply = ',reply)
                    listbox.insert(tkinter.END, reply_txt, 'red')
                elif data2 == user or data3 == user:  # 显示私聊
                    print('Here')
                    listbox.insert(tkinter.END, data1, 'red')  # END将信息加在最后一行 
            listbox.see(tkinter.END)  # 显示在最后
            
        
r = threading.Thread(target=recv)
r.start()  # 开始线程接收信息

root.mainloop()
s.close()  # 关闭图形界面后关闭TCP连接
