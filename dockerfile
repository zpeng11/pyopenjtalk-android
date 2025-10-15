FROM androidsdk/android-31 

# 设置非交互模式，避免 apt 提示
ENV DEBIAN_FRONTEND=noninteractive

# 更新包列表并添加 deadsnakes PPA
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update

# 更新包列表并安装软件包
RUN apt-get update && \
    apt-get install -y \
    git \
    vim \
    patch \
    patchelf \
    wget \
    unzip \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*  # 清理缓存

RUN git clone https://github.com/chaquo/chaquopy.git /app/chaquopy

# 下载并安装 Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3 && \
    rm Miniconda3-latest-Linux-x86_64.sh

# 初始化并创建环境
ENV PATH="/opt/miniconda3/bin:$PATH"

RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
RUN conda init bash && \
    /opt/miniconda3/bin/conda create -n py310 python=3.10 -y

# 默认激活
RUN echo 'conda activate py310' >> ~/.bashrc

SHELL ["/bin/bash", "-c"]
RUN /bin/bash -c "source /opt/miniconda3/etc/profile.d/conda.sh && \
    conda activate py310 && \
    python --version && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r /app/chaquopy/server/pypi/requirements.txt &&\
    pip install numpy==1.25.0 &&\
    pip install setuptools_scm==8.1.0"

# 设置工作目录
WORKDIR /app

# 默认命令：启动 bash
CMD ["/bin/bash","-c","/app/pyopenjtalk/build.sh"]