# Use a base image with Java installed
FROM ubuntu:latest


ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-arm64

# Set environment variables
ENV HADOOP_VERSION=3.3.1
ENV HADOOP_HOME=/usr/local/hadoop
ENV HADOOP_INSTALL=/usr/local/hadoop
ENV HADOOP_MAPRED_HOME=/usr/local/hadoop
ENV HADOOP_COMMON_HOME=/usr/local/hadoop
ENV HADOOP_HDFS_HOME=/usr/local/hadoop
ENV YARN_HOME=/usr/local/hadoop
ENV HADOOP_COMMON_LIB_NATIVE_DIR=/usr/local/hadoop/lib/native
ENV PATH=$PATH:/usr/local/hadoop/sbin:/usr/local/hadoop/bin
ENV HADOOP_OPTS="-Djava.library.path=/usr/local/hadoop/lib/native"
ENV PATH=$PATH:/usr/local/hadoop/bin:/usr/local/hadoop/sbin
ENV HDFS_NAMENODE_USER=root
ENV HDFS_DATANODE_USER=root
ENV HDFS_SECONDARYNAMENODE_USER=root
ENV YARN_RESOURCEMANAGER_USER=root
ENV YARN_NODEMANAGER_USER=root


# Install dependencies
RUN apt-get update && \
    apt-get install -y wget ufw ssh rsync openjdk-8-jdk openssh-server openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Allow SSH connections through the firewall
RUN ufw allow ssh

RUN wget -qO- https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz | tar xvz -C /opt && \
    mv /opt/hadoop-$HADOOP_VERSION $HADOOP_HOME && \
    mkdir $HADOOP_HOME/logs && \
    chown -R root:root $HADOOP_HOME


RUN echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-arm64" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh
RUN echo "export HADOOP_CLASSPATH+=\" \$HADOOP_HOME/lib/*.jar\"" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# Generate SSH keys and set up passwordless SSH
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 700 ~/.ssh && \
    chmod 600 ~/.ssh/authorized_keys

# Create HDFS directories and adjust ownership
RUN mkdir -p /home/hadoop/hdfs/namenode && \
    mkdir -p /home/hadoop/hdfs/datanode && \
    mkdir -p /home/hadoop/data && \
    chown -R root:root /home/hadoop/hdfs
    
# Add Hadoop configuration files
COPY core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml
COPY hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml
COPY mapred-site.xml $HADOOP_HOME/etc/hadoop/mapred-site.xml
COPY yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml

COPY mapper.py /home/hadoop/data/mapper.py
COPY reducer.py /home/hadoop/data/reducer.py
COPY framework.py /home/hadoop/data/framework.py
COPY Train.csv /home/hadoop/data/Train.csv
COPY execut.sh /home/hadoop/data/execut.sh


# Format HDFS
RUN hdfs namenode -format

# Expose Hadoop ports
EXPOSE 9000 9870 9864 9867 19888 8030 8031 8032 8033 8088

# Start Hadoop services
# CMD [ "sh", "-c", "$HADOOP_HOME/sbin/start-all.sh && tail -f /dev/null" ]
CMD service ssh start && \
    $HADOOP_HOME/sbin/start-all.sh && \
    chmod +x /home/hadoop/data/execut.sh && \
    ./home/hadoop/data/execut.sh && \
    tail -f /dev/null


# /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.1.jar
# hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.1.jar -D mapreduce.job.reduces=5 -file mapper.py -mapper "python3 mapper.py" -file reducer.py -reducer "python3 reducer.py" -file framework.py -input input -output output

# hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.1.jar -D mapreduce.job.reduces=1 -file mapper.py -mapper "python3 mapper.py" -file reducer.py -reducer "python3 reducer.py" -input input -output output