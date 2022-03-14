# autoLiter-web
autoLiter-web是一个基于Flask以及sqlite3的文献笔记管理器，基于[autoLiteratur](https://github.com/WilmerWang/autoLiterature)项目。

~~使用以下账户测试本项目:~~  
~~地址：测试机，已经下线~~  
~~账号：test@example.com~~  
~~密码：cat~~  

## 特点
- 自动抓取文献元信息，并下载文献（可选项）
- 标签以及标签分类功能
- 全文搜索功能
- 富文本，可视化更好
- 多用户隔离，公用文献信息


## 安装（Ubuntu）
### 1. 下载软件
```bash
cd ~
git clone https://github.com/WilmerWang/autoLiter_web.git
```

### 2. 环境配置
  - 下载[`sqlite3`](https://sqlite.org/download.html)二进制压缩包，解压并将解压的文件夹目录添加到PATH路径下。
  ```bash
  cd ~
  wget https://sqlite.org/2022/sqlite-tools-linux-x86-3370200.zip

  # 解压到指定路径sulite3
  unzip -d sqlite3 sqlite-tools-linux-x86-3370200.
  
  # 添加到系统环境变量（临时），永久需要写到.bashrc
  export PATH=$PATH:~/sqlite/
  
  # 测试
  sqlte3
  ```
  - 配置python环境变量
  ```bash
  conda create autoliter python=3.8
  conda activate autoliter
  cd ~/autoLiter_web
  pip install -r requirements.txt
  ```
  - 按要求配置[`config.py`](config.py)文件
### 3. 启动软件
```bash
cd ~/autoLiter_web
export FLASK_APP=autoliter.py
export FLASK_DEBUG=1
# 首先新建数据库表
flask shell 
>>> from app import db
>>> db.create_all()
>>> exit()

# 启动软件，默认的端口是5000
flask run --host="0.0.0.0"

# 查看是否启动成功浏览器输入
<your_server_ip>:5000
```

## uwsgi部署
### 1. 初步测试
```bash
sudo apt-get install gcc ngnix

conda activate autoliter
conda install -c conda-forge uwsgi

# 测试
uwsgi --socket 0.0.0.0:5000 --protocol=http -w autoliter:app
```
### 2. uwsgi启动
测试没问题后，新增一个`uwsgi.ini`文件，参考同名文件配置。随后启动
```bash 
uwsgi --ini uwsgi.ini
```
### 3. service启动
配置`autoliter.service`到`/etc/systemd/system/`文件夹
```
sudo systemctl start autoliter.service

# 开机自启
sudo systemctl enable autoliter.service
```


## 其他
### 感谢
感谢flasky项目以及其他相关项目

### TODO
