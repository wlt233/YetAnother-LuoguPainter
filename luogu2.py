import requests
from PIL import Image
import time
import threading
import brotli
from websocket import create_connection


class luogu(threading.Thread):
    def __init__(self, cid, uid):
        threading.Thread.__init__(self)
        self.cid = cid
        self.uid = uid
        self.worklist = []
        self.session = requests.Session()
        self.headers = {
            "accept-encoding":"gzip, deflate, br",
            "accept-language":"zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
            "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
            "cookie":"__client_id=" + self.cid + "; login_referer=https%3A%2F%2Fwww.luogu.com.cn; _uid=" + self.uid,
            "origin":"https://www.luogu.com.cn",
            "referer":"https://www.luogu.com.cn/paintBoard",
            "sec-fetch-mode":"cors",
            "sec-fetch-site":"same-origin",
            "user-agent":"Wlt233's autopaint script",
            "x-requested-with":"XMLHttpRequest"
            }

    def paint(self, x, y, color):
        data = {'x':x,'y':y,'color':color}
        response = self.session.post('https://www.luogu.com.cn/paintBoard/paint', data, headers = self.headers)
        #print (response.content)
        if response.status_code == 200: print(data, "painted by uid = " ,self.uid)
        else: 
            print(data, "failed to paint. uid =" ,self.uid)
            print(response.content)

    def run(self):
        while True:
            time.sleep(1)
            while self.worklist != []:
                pixel = self.worklist.pop()
                self.paint(pixel[0], pixel[1], pixel[2])
                time.sleep(10)


class work(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.colorlist = [[0, 0, 0], [255, 255, 255], [170, 170, 170], [85, 85, 85], [254, 211, 199], [255, 196, 206], [250, 172, 142], [255, 139, 131], [244, 67, 54], [233, 30, 99], [226, 102, 158], [156, 39, 176], [103, 58, 183], [63, 81, 181], [0, 70, 112], [5, 113, 151], [33, 150, 243], [0, 188, 212], [59, 229, 219], [151, 253, 220], [22, 115, 0], [55, 169, 60], [137, 230, 66], [215, 255, 7], [255, 246, 209], [248, 203, 140], [255, 235, 59], [255, 193, 7], [255, 152, 0], [255, 87, 34], [184, 63, 39], [121, 85, 72]]
        self.img_file = r"C:\Users\14861\Desktop\timg1.png"
        self.pixellist = []
        self.worklist = []
        self.userlist = []
        self.usernumber = 0
        self.realmap = []
        self.cookies = [("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "164102")]
        self.startx = 300
        self.starty = 0
        self.picx = 50
        self.picy = 57
    

    def check_pic(self, xstart, ystart):
        im = Image.open(self.img_file)
        self.picx = im.size[0]
        self.picy = im.size[1]

        for x in range(0, self.picx):
            for y in range(0, self.picy):
                R, G, B, A = im.getpixel((x, y))
                if A > 50:
                    mindis = 1000000
                    chosencolor = 1
                    for i in range(0,31):
                        current = (R - self.colorlist[i][0])**2 + (G - self.colorlist[i][1])**2 + (B - self.colorlist[i][2])**2 
                        if current < mindis:
                            mindis = current
                            chosencolor = i
                    self.pixellist.append([xstart + x, ystart + y, chosencolor]) # 300-349=50 / 0-56=57
                    #self.worklist.append([xstart + x, ystart + y, chosencolor])
                #else: self.pixellist.append([xstart + x, ystart + y, 1])
        print ("Check picture finished.")
    
    def add_user(self):
        for user_cookie in self.cookies:
            self.userlist.append(luogu(user_cookie[0], user_cookie[1]))
            print ("User uid = ", user_cookie[1], " created.")
            self.usernumber += 1
    
    def run(self):
        self.check_pic(self.startx, self.starty)
        cmt = cmthread(self)
        cmt.start()
        wst = wsthread(self, self.startx, self.startx, self.picx, self.picy)
        time.sleep(3)
        wst.start()
        time.sleep(0.01)
        self.add_user()
        current_user = 0
        while self.worklist != []:
            pixel = self.worklist.pop()
            self.userlist[current_user].worklist.append(pixel)
            current_user += 1
            if current_user == self.usernumber:
                current_user = 0
        print("First assigned finished.")  
        for users in self.userlist:
            users.start()
            time.sleep(1.3)
        while True:
            if self.worklist != []:
                pixel = self.worklist.pop()
                self.userlist[current_user].worklist.append(pixel)
                current_user += 1
                if current_user == self.usernumber:
                    current_user = 0


class wsthread(threading.Thread):
    def __init__(self, work, xstart, ystart, xlength, ylength):
        threading.Thread.__init__(self)
        self.work = work
        self.xstart = xstart
        self.ystart = ystart
        self.xlength = xlength
        self.ylength = ylength

    def run(self):
        time.sleep(0.01)
        ws = create_connection("wss://ws.luogu.com.cn/ws")
        ws.send('{"type": "join_channel","channel": "paintboard","channel_param": ""}')
        print("Websocket started.")
        while True:
            recv = eval(ws.recv())
            if recv["type"] == "paintboard_update":
                x = recv["x"]
                y = recv["y"]
                self.work.realmap[x][y] = recv["color"]
                if x >= self.xstart and x < self.xstart + self.xlength and y >= self.ystart and y < self.ystart + self.ylength:
                    for pixel in self.work.pixellist:
                        if x == pixel[0] and y == pixel[1]:
                            if self.work.realmap[x][y] != pixel[2]:
                                self.work.worklist.append(pixel)
                                time.sleep(0.01)
                                print (x, y, "is changed...")


class cmthread(threading.Thread):
    def __init__(self, work):
        threading.Thread.__init__(self)
        self.work = work

    def initmap(self):
        headers = {
            "accept-encoding":"gzip, deflate, br",
            "accept-language":"zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
            "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
            "origin":"https://www.luogu.com.cn",
            "referer":"https://www.luogu.com.cn/paintBoard",
            "sec-fetch-mode":"cors",
            "sec-fetch-site":"same-origin",
            "user-agent":"Wlt233's autopaint script",
            "x-requested-with":"XMLHttpRequest"
            }
        session = requests.Session()
        mapinit = session.get("https://www.luogu.com.cn/paintBoard/board", headers = headers)
        #print(str(brotli.decompress(mapinit.content), encoding = "utf8").split("\n"))
        rawmap = str(brotli.decompress(mapinit.content), encoding = "utf8").split("\n")
        for row in rawmap:
            current_row = []
            for char in row:
                if char in "0123456789":
                    current_row.append(int(char))
                else:
                    current_row.append(ord(char) - ord('a') + 10)
            self.work.realmap.append(current_row)
        print ("Init map finished.", end = '')    

    def checkmap(self):
        diff = 0
        for pixle in self.work.pixellist:
            if self.work.realmap[pixle[0]][pixle[1]] != pixle[2]:
                if pixle not in self.work.worklist:
                    self.work.worklist.append(pixle)
                diff += 1
        print("Check different finished. Found", diff, "difference(s).")

    def run(self):
        self.initmap()
        self.checkmap()
        while True:
            self.initmap()
            self.checkmap()
            time.sleep(30)



w = work()
w.start()




            
            
            
            
            

