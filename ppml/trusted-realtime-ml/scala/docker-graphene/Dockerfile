ARG BIGDL_VERSION=2.1.0-SNAPSHOT
ARG SPARK_VERSION=3.1.2

# stage.1 graphene
FROM ubuntu:20.04 AS graphene
ARG GRAPHENE_BRANCH=branch-1.2-rc1
RUN env DEBIAN_FRONTEND=noninteractive apt-get update && \
    env DEBIAN_FRONTEND=noninteractive apt-get install -y \
        autoconf bison build-essential coreutils gawk git wget \
        python3 python3-pip libcurl4-openssl-dev \
        libprotobuf-c-dev protobuf-c-compiler python3-protobuf wget
RUN git clone https://github.com/analytics-zoo/graphene.git /graphene
RUN cd /graphene && \
    git fetch origin $GRAPHENE_BRANCH && \
    git checkout $GRAPHENE_BRANCH
RUN pip3 install ninja meson && \
    python3 -m pip install toml==0.10.2 click jinja2
RUN cd /graphene/Pal/src/host/Linux-SGX && \
    git clone https://github.com/intel/SGXDataCenterAttestationPrimitives.git linux-sgx-driver && \
    cd linux-sgx-driver && \
    git checkout DCAP_1.7 && \
    cp -r driver/linux/* .
RUN cd /graphene && \
    make && \
    ISGX_DRIVER_PATH=/graphene/Pal/src/host/Linux-SGX/linux-sgx-driver make -s -j4 SGX=1 && \
    meson setup build/ --prefix="/graphene/meson_build_output" \ 
    --buildtype=release -Ddirect=enabled -Dsgx=enabled  && \
    ninja -C build/ && \
    ninja -C build/ install
RUN /graphene/Scripts/download --output redis.tar.gz --sha256 f7ded6c27d48c20bc78e797046c79b6bc411121f0c2d7eead9fea50d6b0b6290 --url https://github.com/antirez/redis/archive/6.0.5.tar.gz
RUN for f in $(find /graphene/Runtime -type l); do cp --remove-destination $(realpath $f) $f; done

# stage.2 jdk & scala & flink
FROM ubuntu:20.04 as flink
ARG FLINK_VERSION=1.11.3
ARG SCALA_VERSION=2.12
ARG SCALA_SUB_VERSION_NUM=10
ARG JDK_VERSION=8u192
ARG JDK_URL=your_jdk_url
ENV FLINK_VERSION ${FLINK_VERSION}
ENV SCALA_VERSION ${SCALA_VERSION}
ENV SCALA_SUB_VERSION_NUM ${SCALA_SUB_VERSION_NUM}

RUN apt-get update --fix-missing && \
    env DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y tzdata apt-utils wget unzip
# java
RUN wget $JDK_URL && \
    gunzip jdk-$JDK_VERSION-linux-x64.tar.gz && \
    tar -xf jdk-$JDK_VERSION-linux-x64.tar -C /opt && \
    rm jdk-$JDK_VERSION-linux-x64.tar && \
    mv /opt/jdk* /opt/jdk$JDK_VERSION && \
    ln -s /opt/jdk$JDK_VERSION /opt/jdk
# scala
RUN cd / && wget -c https://downloads.lightbend.com/scala/${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}/scala-${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}.tgz && \
    (cd / && gunzip < scala-${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}.tgz)|(cd /opt && tar -xvf -) && \
    rm /scala-${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}.tgz
# flink
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
RUN ls -al /opt

# stage.3 bigdl
FROM ubuntu:20.04 as bigdl
ARG BIGDL_VERSION
ARG SPARK_VERSION
ENV SPARK_VERSION		${SPARK_VERSION}
ENV BIGDL_VERSION		${BIGDL_VERSION}
ENV BIGDL_HOME		        /bigdl-${BIGDL_VERSION}
ADD ./download-bigdl-serving.sh /opt/download-bigdl-serving.sh
RUN apt-get update --fix-missing && \
    apt-get install -y apt-utils curl wget unzip git
RUN wget https://raw.githubusercontent.com/intel-analytics/analytics-zoo/bigdl-2.0/docker/hyperzoo/download-bigdl.sh && \
    chmod a+x ./download-bigdl.sh && \
    chmod a+x /opt/download-bigdl-serving.sh
RUN ./download-bigdl.sh && \
    rm bigdl*.zip && \
    cd /opt && \
    ./download-bigdl-serving.sh
RUN cd /opt && \
    wget https://raw.githubusercontent.com/intel-analytics/BigDL/branch-2.0/scala/serving/scripts/perf-benchmark/e2e_throughput.py && \
    wget https://raw.githubusercontent.com/intel-analytics/BigDL/branch-2.0/scala/serving/scripts/perf-benchmark/requirement.yml && \
    wget -c "https://sourceforge.net/projects/analytics-zoo/files/analytics-zoo-data/ILSVRC2012_val_00000001.JPEG/download" -O ILSVRC2012_val_00000001.JPEG && \
    mkdir resnet50 && \
    cd resnet50 && \
    wget -c "https://sourceforge.net/projects/analytics-zoo/files/analytics-zoo-models/openvino/2018_R5/resnet_v1_50.bin/download" -O resnet_v1_50.bin && \
    wget -c "https://sourceforge.net/projects/analytics-zoo/files/analytics-zoo-models/openvino/2018_R5/resnet_v1_50.xml/download" -O resnet_v1_50.xml


# stage.4 ppml
FROM ubuntu:20.04
ARG BIGDL_VERSION
ARG SPARK_VERSION
ARG SCALA_VERSION=2.12
ARG SCALA_SUB_VERSION_NUM=10
ARG FLINK_VERSION=1.11.3
ENV SPARK_VERSION			${SPARK_VERSION}
ENV BIGDL_VERSION			${BIGDL_VERSION}
ENV JAVA_HOME				/opt/jdk8
ENV PATH				/graphene/meson_build_output/bin:${JAVA_HOME}/bin:${PATH}
ENV LOCAL_IP				127.0.0.1
ENV SGX_MEM_SIZE			64G
ENV REDIS_PORT				6379
ENV FLINK_VERSION			${FLINK_VERSION}
ENV FLINK_HOME				/ppml/trusted-realtime-ml/java/work/flink-${FLINK_VERSION}
ENV FLINK_JOB_MANAGER_IP		127.0.0.1
ENV FLINK_JOB_MANAGER_REST_PORT		8081
ENV FLINK_JOB_MANAGER_RPC_PORT		6123
ENV FLINK_TASK_MANAGER_IP		127.0.0.1
ENV FLINK_TASK_MANAGER_DATA_PORT	6126
ENV FLINK_BLOB_SERVER_PORT              6124
ENV FLINK_TASK_MANAGER_RPC_PORT		6125
ENV FLINK_TASK_MANAGER_TASKSLOTS_NUM	1
ENV CORE_NUM                            2
ENV TASKMANAGER_MEMORY_TASK_HEAP_SIZE   10gb
ENV TASKMANAGER_MEMORY_MANAGED_SIZE     8192mb
ENV XMX_SIZE                            10g 
ENV SGX_MODE                            sgx
ENV REDIS_HOST                          127.0.0.1
ENV SCALA_VERSION                       ${SCALA_VERSION}
ENV SCALA_SUB_VERSION_NUM               ${SCALA_SUB_VERSION_NUM}

RUN mkdir -p /graphene && \
    mkdir -p /graphene/Runtime && \
    mkdir -p /graphene/python && \
    mkdir -p /graphene/Tools && \
    mkdir -p /graphene/Pal/src && \
    mkdir -p /graphene/meson_build_output && \
    mkdir -p /ppml/trusted-realtime-ml/redis && \
    mkdir -p /ppml/trusted-realtime-ml/redis/work/keys && \
    mkdir -p /ppml/trusted-realtime-ml/redis/work/password && \
    mkdir -p /ppml/trusted-realtime-ml/java/work && \
    mkdir -p /ppml/trusted-realtime-ml/java/work/keys && \
    mkdir -p /ppml/trusted-realtime-ml/java/work/password && \
    mkdir -p /ppml/trusted-realtime-ml/java/work/data && \
    mkdir -p /ppml/trusted-realtime-ml/java/work/models && \
    mkdir -p /ppml/trusted-realtime-ml/java/work/benchmark && \
    mkdir -p /root/.keras/datasets && \
    mkdir -p /root/.zinc && \
    mkdir -p /root/.m2 && \
    mkdir -p /graphene/Pal/src/host/Linux-SGX/signer

COPY --from=graphene /graphene/Scripts /graphene/Scripts
COPY --from=graphene /graphene/Runtime/ /graphene/Runtime
COPY --from=graphene /graphene/python /graphene/python
COPY --from=graphene /graphene/Pal /graphene/Pal
COPY --from=graphene /graphene/Pal/src/host/Linux-SGX/generated_offsets.py /graphene/python/
COPY --from=graphene /graphene/Tools/argv_serializer /graphene/Tools
COPY --from=graphene /graphene/meson_build_output /graphene/meson_build_output
COPY --from=graphene /redis.tar.gz /ppml/trusted-realtime-ml/redis
COPY --from=flink /opt/jdk  /opt/jdk8
COPY --from=flink /opt/scala-${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}  /opt/scala-${SCALA_VERSION}.${SCALA_SUB_VERSION_NUM}
COPY --from=flink /opt/flink-${FLINK_VERSION} /ppml/trusted-realtime-ml/java/work/flink-${FLINK_VERSION}
COPY --from=bigdl /opt/bigdl-serving*-jar-with-dependencies.jar /ppml/trusted-realtime-ml/java/work/bigdl-serving-jar-with-dependencies.jar
COPY --from=bigdl /opt/bigdl-serving*-http.jar /ppml/trusted-realtime-ml/java/work/bigdl-serving-http.jar
COPY --from=bigdl /opt/resnet50/ /ppml/trusted-realtime-ml/java/work/models/resnet50
COPY --from=bigdl /opt/ILSVRC2012_val_00000001.JPEG /ppml/trusted-realtime-ml/java/work/data/ILSVRC2012_val_00000001.JPEG
COPY --from=bigdl /opt/e2e_throughput.py /ppml/trusted-realtime-ml/java/work/benchmark/e2e_throughput.py
COPY --from=bigdl /opt/requirement.yml /ppml/trusted-realtime-ml/java/work/benchmark/requirement.yml

RUN apt-get update --fix-missing && \
    env DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y tzdata && \
    apt-get install -y apt-utils vim curl nano wget unzip git tree && \
    apt-get install -y libsm6 make build-essential && \
    apt-get install -y autoconf gawk bison libcurl4-openssl-dev python3-protobuf libprotobuf-c-dev protobuf-c-compiler && \
    apt-get install -y openssl libssl-dev pkg-config && \
    apt-get install -y netcat net-tools && \
    apt-get install -y python3-minimal && \
    apt-get install -y build-essential python3 python3-setuptools python3-dev python3-pip && \
    pip3 install --upgrade pip && \
    pip install --upgrade setuptools && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip install --no-cache-dir ninja meson && \
    python3 -m pip install toml==0.10.2 click jinja2

RUN mkdir -p /ppml/trusted-realtime-ml/redis/src && \
    tar -C /ppml/trusted-realtime-ml/redis/src --strip-components=1 -xf /ppml/trusted-realtime-ml/redis/redis.tar.gz && \
    make BUILD_TLS=yes -C /ppml/trusted-realtime-ml/redis/src && \
    cp /ppml/trusted-realtime-ml/redis/src/src/redis-server /ppml/trusted-realtime-ml/redis/redis-server

ADD ./Makefile /ppml/trusted-realtime-ml/redis/Makefile
ADD ./bash.manifest.template /ppml/trusted-realtime-ml/redis/bash.manifest.template
ADD ./init.sh /ppml/trusted-realtime-ml/redis/init.sh
ADD ./clean.sh /ppml/trusted-realtime-ml/redis/clean.sh
ADD ./start-redis.sh /ppml/trusted-realtime-ml/redis/start-redis.sh
ADD ./Makefile /ppml/trusted-realtime-ml/java/Makefile
ADD ./bash.manifest.template /ppml/trusted-realtime-ml/java/bash.manifest.template
ADD ./init.sh /ppml/trusted-realtime-ml/java/init.sh
ADD ./clean.sh /ppml/trusted-realtime-ml/java/clean.sh
ADD ./start-flink-jobmanager.sh /ppml/trusted-realtime-ml/java/start-flink-jobmanager.sh
ADD ./start-flink-taskmanager.sh /ppml/trusted-realtime-ml/java/start-flink-taskmanager.sh
ADD ./start-http-frontend.sh /ppml/trusted-realtime-ml/java/start-http-frontend.sh
ADD ./servables.yaml /ppml/trusted-realtime-ml/java/work/servables.yaml
ADD ./init-cluster-serving.sh /ppml/trusted-realtime-ml/java/init-cluster-serving.sh
ADD ./start-cluster-serving-job.sh /ppml/trusted-realtime-ml/java/start-cluster-serving-job.sh
ADD ./check-status.sh /ppml/trusted-realtime-ml/check-status.sh
ADD ./start-all.sh /ppml/trusted-realtime-ml/start-all.sh
ADD ./init-benchmark.sh /ppml/trusted-realtime-ml/java/work/benchmark/init-benchmark.sh
ADD ./cluster-serving-config.yaml /ppml/trusted-realtime-ml/java/config.yaml

RUN chmod a+x /ppml/trusted-realtime-ml/redis/init.sh && \
    chmod a+x /ppml/trusted-realtime-ml/redis/clean.sh && \
    chmod a+x /ppml/trusted-realtime-ml/redis/start-redis.sh && \
    chmod a+x /ppml/trusted-realtime-ml/java/init.sh && \
    chmod a+x /ppml/trusted-realtime-ml/java/clean.sh && \
    chmod a+x /ppml/trusted-realtime-ml/java/start-flink-jobmanager.sh && \
    chmod a+x /ppml/trusted-realtime-ml/java/start-flink-taskmanager.sh && \
    chmod a+x /ppml/trusted-realtime-ml/java/start-http-frontend.sh && \
    chmod a+x /ppml/trusted-realtime-ml/java/init-cluster-serving.sh && \
    chmod a+x /ppml/trusted-realtime-ml/java/start-cluster-serving-job.sh && \
    chmod a+x /ppml/trusted-realtime-ml/check-status.sh && \
    chmod a+x /ppml/trusted-realtime-ml/start-all.sh

ENV PYTHONPATH	${PYTHONPATH}:/graphene/meson_build_output/lib/python3.8/site-packages
ENV LC_ALL	C.UTF-8
ENV LANG	C.UTF-8
