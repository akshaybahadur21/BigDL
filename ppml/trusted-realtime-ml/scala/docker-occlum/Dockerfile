ARG BIGDL_VERSION=2.1.0-SNAPSHOT
ARG SPARK_VERSION=3.1.2
ARG FLINK_VERSION=1.11.3
ARG SCALA_VERSION=2.12
ARG SCALA_SUB_VERSION_NUM=10

# stage.1 Redis
FROM ubuntu:20.04 as redis-tls

WORKDIR /opt

RUN apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
        pkg-config git build-essential coreutils ca-certificates && \
    apt-get clean

RUN git clone https://github.com/openssl/openssl.git && \
    cd openssl && \
    git checkout tags/OpenSSL_1_1_1 -b OpenSSL_1_1_1 && \
    ./config \
    --openssldir=/opt/ssl \
    --with-rand-seed=rdcpu \
    no-zlib no-async no-tests && \
    make -j `getconf _NPROCESSORS_ONLN` && make install

RUN git clone https://github.com/redis/redis.git && \
    cd redis && \
    git checkout 6.0.6 && \
    make -j `getconf _NPROCESSORS_ONLN` BUILD_TLS=yes && make PREFIX=/opt/redis install

# stage. 2 Flink & bigdl & Scala
FROM ubuntu:20.04 as bigdl
ENV JAVA_HOME				/usr/lib/jvm/java-8-openjdk-amd64
ARG FLINK_VERSION
ENV FLINK_VERSION ${FLINK_VERSION}
ENV FLINK_HOME				/opt/flink-${FLINK_VERSION}
ARG BIGDL_VERSION
ENV BIGDL_VERSION=${BIGDL_VERSION}
ARG SPARK_VERSION
ARG SCALA_VERSION
ARG SCALA_SUB_VERSION_NUM
ENV BIGDL_HOME		        /opt/bigdl-${BIGDL_VERSION}
ENV SCALA_VERSION ${SCALA_VERSION}
ENV SCALA_SUB_VERSION_NUM ${SCALA_SUB_VERSION_NUM}

RUN apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
        ca-certificates wget unzip apt-utils curl && \
    apt-get clean

# scala
RUN cd / && wget -c https://downloads.lightbend.com/scala/${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}/scala-${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}.tgz && \
    (cd / && gunzip < scala-${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}.tgz)|(cd /opt && tar -xvf -) && \
    rm /scala-${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}.tgz

# Download flink
RUN cd /opt && \
    wget https://archive.apache.org/dist/flink/flink-${FLINK_VERSION}/flink-${FLINK_VERSION}-bin-scala_${SCALA_VERSION}.tgz && \
    tar -zxvf flink-${FLINK_VERSION}-bin-scala_${SCALA_VERSION}.tgz && \
    rm flink-${FLINK_VERSION}-bin-scala_${SCALA_VERSION}.tgz && \
    rm /opt/flink-${FLINK_VERSION}/lib/log4j-1.2-api-2.12.1.jar && \
    rm /opt/flink-${FLINK_VERSION}/lib/log4j-api-2.12.1.jar && \
    rm /opt/flink-${FLINK_VERSION}/lib/log4j-core-2.12.1.jar && \
    rm /opt/flink-${FLINK_VERSION}/lib/log4j-slf4j-impl-2.12.1.jar && \
    wget -P /opt/flink-${FLINK_VERSION}/lib/ https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-1.2-api/2.17.1/log4j-1.2-api-2.17.1.jar && \
    wget -P /opt/flink-${FLINK_VERSION}/lib/ https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-api/2.17.1/log4j-api-2.17.1.jar && \
    wget -P /opt/flink-${FLINK_VERSION}/lib/ https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-core/2.17.1/log4j-core-2.17.1.jar && \
    wget -P /opt/flink-${FLINK_VERSION}/lib/ https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-slf4j-impl/2.17.1/log4j-slf4j-impl-2.17.1.jar

# Download bigdl
RUN cd /opt && \
    wget https://raw.githubusercontent.com/intel-analytics/BigDL/branch-2.0/ppml/trusted-realtime-ml/scala/docker-graphene/download-bigdl-serving.sh && \
    chmod a+x download-bigdl-serving.sh && \
    ./download-bigdl-serving.sh

# models
RUN cd /opt && \
    mkdir resnet50 && \
    cd resnet50 && \
    wget -c "https://sourceforge.net/projects/analytics-zoo/files/analytics-zoo-models/openvino/2018_R5/resnet_v1_50.bin/download" -O resnet_v1_50.bin && \
    wget -c "https://sourceforge.net/projects/analytics-zoo/files/analytics-zoo-models/openvino/2018_R5/resnet_v1_50.xml/download" -O resnet_v1_50.xml
# data and scripts for kubernets
RUN cd /opt && \
    wget https://raw.githubusercontent.com/intel-analytics/BigDL/branch-2.0/scala/serving/scripts/perf-benchmark/requirement.yml && \
    wget -c "https://sourceforge.net/projects/analytics-zoo/files/analytics-zoo-data/ILSVRC2012_val_00000001.JPEG/download" -O ILSVRC2012_val_00000001.JPEG

# stage.3 az ppml occlum
FROM occlum/occlum:0.27.0-ubuntu20.04 as ppml

ARG FLINK_VERSION
ARG BIGDL_VERSION
ARG SCALA_VERSION
ARG SCALA_SUB_VERSION_NUM


ENV JAVA_HOME				/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH                    ${JAVA_HOME}/bin:${PATH}
ENV LOCAL_IP				127.0.0.1
ENV SGX_MEM_SIZE			32G
ENV REDIS_PORT				6379
ENV FLINK_VERSION			${FLINK_VERSION}
ENV FLINK_HOME				/opt/flink-${FLINK_VERSION}
ENV BIGDL_HOME		        /opt/bigdl-${BIGDL_VERSION}
ENV FLINK_JOB_MANAGER_IP		127.0.0.1
ENV FLINK_JOB_MANAGER_REST_PORT		8081
ENV FLINK_JOB_MANAGER_RPC_PORT		6123
ENV FLINK_TASK_MANAGER_IP		127.0.0.1
ENV FLINK_TASK_MANAGER_DATA_PORT	6124
ENV FLINK_TASK_MANAGER_RPC_PORT		6125
ENV FLINK_TASK_MANAGER_TASKSLOTS_NUM	1
ENV CORE_NUM                            2
ENV SCALA_VERSION                       ${SCALA_VERSION}
ENV SCALA_SUB_VERSION_NUM               ${SCALA_SUB_VERSION_NUM}

RUN mkdir -p ${BIGDL_HOME}


COPY --from=redis-tls /opt/ssl /opt/ssl
COPY --from=redis-tls /opt/redis /opt/redis
COPY --from=bigdl /opt/scala-${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}  /opt/scala-${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}
COPY --from=bigdl /opt/flink-${FLINK_VERSION} /opt/flink-${FLINK_VERSION}
COPY --from=bigdl /opt/resnet50 /opt/resnet50
COPY --from=bigdl /opt/bigdl-serving*-jar-with-dependencies.jar ${BIGDL_HOME}/bigdl-serving-jar-with-dependencies.jar
COPY --from=bigdl /opt/bigdl-serving*-http.jar ${BIGDL_HOME}/bigdl-serving-http.jar

# RUN apt-get update && \
#     DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
#         build-essential ca-certificates openjdk-11-jdk \
#         curl tzdata wget netcat gnupg2 jq make gdb libfuse-dev libtool \
#         libprotobuf-c-dev protobuf-c-compiler libcurl4-openssl-dev libprotobuf-dev
# Add 01.org & key
# RUN echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu bionic main' | tee /etc/apt/sources.list.d/intelsgx.list && \
#     wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | apt-key add -

# RUN echo 'deb [arch=amd64] https://occlum.io/occlum-package-repos/debian bionic main' | tee /etc/apt/sources.list.d/occlum.list && \
#     wget -qO - https://occlum.io/occlum-package-repos/debian/public.key | apt-key add -

# RUN apt-get update && \
#     DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
#         build-essential ca-certificates openjdk-11-jdk curl wget netcat net-tools \
#         gnupg2 vim jq make gdb libfuse-dev libtool \
#         libsgx-dcap-ql libsgx-epid libsgx-urts libsgx-quote-ex libsgx-uae-service \
#         libsgx-dcap-quote-verify-dev \
#         occlum && \
#     apt-get clean

# RUN echo "source /etc/profile" >> $HOME/.bashrc 

RUN apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
        build-essential ca-certificates openjdk-11-jdk \
        curl wget netcat net-tools && \
    apt-get clean

# Cluster Serving config
ADD ./cluster-serving-config.yaml /opt/config.yaml
ADD ./servables.yaml /opt/servables.yaml
# PPML scripts
ADD ./init-occlum-taskmanager.sh /opt/init-occlum-taskmanager.sh
ADD ./start-redis.sh /opt/start-redis.sh
ADD ./check-status.sh /opt/check-status.sh
ADD ./start-flink-jobmanager.sh /opt/start-flink-jobmanager.sh
ADD ./start-flink-taskmanager.sh /opt/start-flink-taskmanager.sh
ADD ./start-cluster-serving-job.sh /opt/start-cluster-serving-job.sh
ADD ./start-http-frontend.sh /opt/start-http-frontend.sh
ADD ./start-all.sh /opt/start-all.sh
ADD ./init-cluster-serving.sh /opt/init-cluster-serving.sh
ADD ./init-benchmark.sh /opt/init-benchmark.sh
ADD ./e2e_throughput.py /opt/e2e_throughput.py

RUN chmod a+x /opt/init-occlum-taskmanager.sh && \
    chmod a+x /opt/start-redis.sh && \
    chmod a+x /opt/check-status.sh && \
    chmod a+x /opt/start-flink-jobmanager.sh && \
    chmod a+x /opt/start-flink-taskmanager.sh && \
    chmod a+x /opt/start-cluster-serving-job.sh && \
    chmod a+x /opt/start-http-frontend.sh && \
    chmod a+x /opt/start-all.sh && \
    chmod a+x /opt/init-cluster-serving.sh && \
    chmod a+x /opt/config.yaml && \
    chmod a+x /opt/init-benchmark.sh && \
    chmod a+x /opt/e2e_throughput.py
