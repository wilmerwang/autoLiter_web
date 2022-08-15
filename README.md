# autoLiter-web
autoLiter-web是一个基于Flask以及sqlite3的文献笔记管理器，基于[autoLiteratur](https://github.com/WilmerWang/autoLiterature)项目。 

## 特点
- 自动抓取文献元信息，并下载文献（可选项）
- 标签以及标签分类功能
- 全文搜索功能
- Markdown编辑
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
  unzip sqlite-tools-linux-x86-3370200.zip && mv sqlite-tools-linux-x86-3370200 sqlite3
  
  # 添加到系统环境变量（临时），永久需要写到.bashrc
  export PATH=$PATH:~/sqlite3/
  
  # 测试
  sqlite3
  ```
  - 配置python环境变量
  ```bash
  conda create autoliter python=3.8
  conda activate autoliter
  cd ~/autoLiter_web
  pip install -r requirements.txt
  ```
  - 按要求配置[`config.py`](config.py)文件
  ```bash
  cp config_publication.py config.py
  # 修改config.py里的邮箱、授权码以及其他个人选项
  ```

  - 配置app/templates/index.html
  ```
  # 可以添加其他图片
  <div class="swiper-slide"><img src="{{ url_for('static', filename='indexImage/10.jpeg') }}"></div>
  
  ```

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
# 方法一
sudo apt-get install gcc ngnix

conda activate autoliter
conda install -c conda-forge uwsgi

# 方法二 或者conda 离线安装
下载 https://uwsgi-docs.readthedocs.io/en/latest/Changelog-2.0.20.html
cd /usr/local # 进入安装目录
tar zxvf uwsg*.gz # 解压文件夹
cd uwsgi*
make

# 测试
uwsgi --socket 0.0.0.0:5000 --protocol=http -w autoliter:app -H ~/anaconda3/envs/autoliter
```
### 2. uwsgi启动
测试没问题后，新增一个`uwsgi.ini`文件，参考同名文件配置。随后启动
```bash 
# 启动
uwsgi --ini uwsgi.ini
# 停止
uwsgi --stop uwsgi.pid
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
- 感谢flasky项目
- 感谢editor.md开源项目
- 感谢其他相关项目


### TODO
- [ ] 本地图片上传
- [ ] PDF私有化以及PDF可编辑
- [ ] 增加通过title下载
- [ ] meta_pdf等信息下载之后，手动下载界面应当固定信息
- [ ] 长文章折叠
- [ ] 改进note 标签输入框
- [x] tags词云
- [x] 主页轮播
 
### 测试文献
#### doi
- 10.1038/s41467-022-29269-6
- 10.1038/s41592-022-01560-w
- 10.1038/s41592-022-01549-5
- 10.1093/bib/bbw139

#### Arxiv id
- 2208.06366
- 2208.06175
- 2208.06049

#### biorxiv or medrxiv id
- 10.1101/2022.07.15.500158 
- 10.1101/2022.01.16.473385 
- 10.1101/2022.08.10.22278638
- 10.1101/2020.04.28.20082677

#### 手动上传信息 (无doi,比如新发布的会议文章)
```
Title: Learning Modulated Loss for Rotated Object Detection
Paper ID: Learning Modulated Loss for Rotated Object Detection
Journal: AAAI21
Paper Link: https://ojs.aaai.org/index.php/AAAI/article/view/16347
PDF Link Online: https://ojs.aaai.org/index.php/AAAI/article/view/16347/16154
```
