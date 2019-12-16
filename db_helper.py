from pymysql import connect
from sshtunnel import SSHTunnelForwarder

# 指定SSH远程跳转
server = SSHTunnelForwarder(ssh_address_or_host=('182.254.162.215', 22),  # 指定SSH中间登录地址和端口号
                            ssh_username='root',  # 指定地址B的SSH登录用户名
                            ssh_password='`Id310106199409200014',  # 指定地址B的SSH登录密码
                            local_bind_address=('127.0.0.1', 3306),
                            # 绑定本地地址A（默认127.0.0.1）及与B相通的端口（根据网络策略配置，若端口全放，则此行无需配置，使用默认即可）
                            remote_bind_address=('172.16.128.8', 3306)  # 指定最终目标C地址，端口号为mysql默认端口号3306
                            )

server.start()
# 打印本地端口，以检查是否配置正确
print(server.local_bind_port)

# 设置mysql连接参数，地址与端口均必须设置为本地地址与端口
# 用户名和密码以及数据库名根据自己的数据库进行配置
db = connect(host="127.0.0.1", port=server.local_bind_port, user="root", passwd="1qaz2wsx", db="dzdp")

cursor = db.cursor()

sql = "select COUNT(1) from test"

try:
    # 执行SQL语句检查是否连接成功
    cursor.execute("SELECT VERSION()")
    result = cursor.fetchone()
    print("Database version : %s " % result)
    # 执行查询语句
    cursor.execute(sql)
    result = cursor.fetchone()
    print("sql result : %s" % result)
except:
    print("Error: unable to fetch data")

# 关闭连接
db.close()
server.close()
