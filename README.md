[opentsdb官网:http://opentsdb.net/overview.html](http://opentsdb.net/overview.html) <br>
欢迎关注[我的简书](https://www.jianshu.com/u/224f57c4918e)<br>
    OpenTSDB是一个基于HBase的分布式、可伸缩的开源时序数据库。OpenTSDB由TSD（Time Series Daemon）和一系列命令行工具组成。TSD用于接收用户请求并将时序数据存储在HBase中。TSD之间是相互独立的，没有master，也没有共享状态，因此可以根据系统的负载情况任意进行扩展。下图是一个基于OpenTSDB的监控系统架构图（来自官方文档）

![image.png](https://upload-images.jianshu.io/upload_images/14788851-49055ba9d883e66d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

由上图可知，opentsdb是基于hbase的上层应用。所以在安装opentsdb时先安装hbase。
# 一、Hbase安装
（略...想不到吧）

# 二、OpenTSDB安装
本文opentsdb安装基于docker,需要了解更多docker安装使用信息请教度娘吧。这里假设已安装好docker，进入docker容器中操作了。opentsdb默认端口4242。
官方也有提供了[opentsdb-docker](https://hub.docker.com/r/petergrace/opentsdb-docker/)镜像。但不是我想要的(不需要在docker启动hbase,只需hbase客户端)，我的hbase集群已安装在宿主机上了，不想修改已有的镜像，自己造。
实践过程中遇到如下错误：
Failed to get D-Bus connection: Operation not permitted
解决办法就是在docker run 的时候运行/usr/sbin/init 。比如：
[root@localhost /]# docker run -tid --name hadoopbase centos/hadoopbase:v001 /usr/sbin/init

### 1、安装jdk环境
<br>`#tar -zxvf jdk-8u181-linux-x64.tar.gz -C /usr/local/java/`
<br>`#vi /etc/profile`
<br>`export JAVA_HOME=/usr/local/java/jdk1.8.0_181`
<br>`export JRE_HOME=$JAVA_HOME/jre`
<br>`export CLASSPATH=.:$JAVA_HOME/lib:$JAVA_HOME/jre/lib`
<br>`export PATH=$PATH:$JAVA_HOME/bin`<br>
### 2、hbase客户端安装
重宿主机拷贝一份hbase过即可，在宿主机上执行
<br>`docker cp /opt/apps/hbase-1.1.1 [容器ID]:/opt/`<br>
### 3、安装GnuPlot
GnuPlot是一个命令行的交互式绘图工具，OpenTSDB使用GnuPlot绘图。
<br>`yum install -y gnuplot`<br>
### 4、下载安装opentsdb
可先到opentsdb官网找到自己想要的版本复制链接
<br>`wget https://github.com/OpenTSDB/opentsdb/releases/download/v2.3.1/opentsdb-2.3.1.noarch.rpm`<br>
`rpm -ivh opentsdb-2.3.1.noarch.rpm`<br>
若报/etc/rc.d/init.d/functions: No such file or directory 错误，解决：yum install initscripts
### 5、检测安装
<br>`#tsdb version`<br>
打印如下
net.opentsdb.tools 2.3.1 built at revision  (MODIFIED)
Built on 2018/05/22 17:08:21 +0000 by root@centos.localhost:/root/rpmbuild/BUILD/opentsdb-2.3.1

### 6、修改配置
至少修改以下两项，其他配置根据需要修改(提示：记得配置主机名映射)
<br>`#vi /etc/opentsdb/opentsdb.conf`<br>
`tsd.core.auto_create_metrics = true`<br>
`tsd.storage.hbase.zk_quorum = hdc-data1,hdc-data2,hdc-data3`<br>
### 7、创建hbase表
COMPRESSION=SNAPPY采用snappy压缩算法，若没安装该算法需自行安装。若不想使用压缩COMPRESSION=NONE 。HBASE_HOME为hbase客户端路径
<br>`env COMPRESSION=SNAPPY HBASE_HOME=/opt/hbase-1.1.1 /usr/share/opentsdb/tools/create_table.sh`<br>
执行之后，会在HBase中创建出tsdb、tsdb-uid、tsdb-tree和tsdb-meta四个表。
### 8、启动及验证
<br>`tsdb tsd &`<br>
<br>`ss -lnt | grep 4242`<br>
<br>`ps aux|grep opentsdb`<br>
### 9、opentsdb使用
创建metric
使用如下命令
<br>`tsdb mkmetric sys.cpu.user`<br>
写入数据
作为测试，我们可以使用telnet接口写入两条数据：
<br>`# telnet localhost 4242`<br>
`Trying 127.0.0.1...`<br>
`Connected to localhost.`<br>
`Escape character is '^]'.`<br>
`put sys.cpu.user 1356998400 42.5 host=webserver01 cpu=0`<br>
`put sys.cpu.user 1356999400 42.7 host=webserver01 cpu=0`<br>
读取数据
可以使用命令行读取刚才写入的两条数据：
<br>`# tsdb query 1356998400 1356999400 sum sys.cpu.user`<br>
`sys.cpu.user 1356998400000 42.500000 {host=webserver01, cpu=0}`<br>
`sys.cpu.user 1356999400000 42.700001 {host=webserver01, cpu=0}`<br>

### 10、web-ui绘图
图一（docker中的opentsdb）
![image.png](https://upload-images.jianshu.io/upload_images/14788851-02bf78ecbf300363.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

opentsdb可以安装很多个，他们共用hbase表。若想考虑负载均衡可结合第三方组件实现。但一般情况足够了。而且opentsdb自带的图形界面一个字，丑。所以采用更美观一点的Grafana监控平台。

# 三、安装Grafana
好文档都在[官网:https://grafana.com/grafana/download](https://grafana.com/grafana/download)
重新建一个docker容器，若需要。grafana默认端口3000
### 1、下载安装
<br>`wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-5.3.2-1.x86_64.rpm`<br>
`sudo yum localinstall grafana-5.3.2-1.x86_64.rpm`<br>
### 2、启动
<br>`service grafana-server start`<br>
### 3、webUI使用
默认用户名：admin，密码：admin
![image.png](https://upload-images.jianshu.io/upload_images/14788851-8ddb3ddeef569c0f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

创建数据源
![image.png](https://upload-images.jianshu.io/upload_images/14788851-a185569741cd2d72.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
点击保存后如提示则数据源正常
![image.png](https://upload-images.jianshu.io/upload_images/14788851-095b8610d774044c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

创建仪表盘
![image.png](https://upload-images.jianshu.io/upload_images/14788851-8e6cc789b68094a2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![image.png](https://upload-images.jianshu.io/upload_images/14788851-94fd5fdb5fd1a01c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


