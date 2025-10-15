#!/bin/bash
# build.sh: 更新 meta.yaml 的 version 从 setup.py

set -e  # 退出 on error
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate py310
cd /app/chaquopy && \
./target/download-target.sh maven/com/chaquo/python/target/3.10.6-1 &&\
mkdir -p /app/chaquopy/server/pypi/packages/pyopenjtalk

cd "$(dirname "$0")"  # 切换到脚本目录（项目根）

version=$(python setup.py --version | tail -1)
echo "Detected version: $version"

python -c "
import yaml
with open('meta.yaml', 'r') as f:
    d = yaml.safe_load(f)
d['package']['version'] = '$version'
with open('/app/chaquopy/server/pypi/packages/pyopenjtalk/meta.yaml', 'w') as f:
    yaml.dump(d, f, default_flow_style=False, indent=2)
print('Updated /app/chaquopy/server/pypi/packages/pyopenjtalk/meta.yaml')
"

cd /app/chaquopy/server/pypi

./build-wheel.py --python 3.10 --abi arm64-v8a pyopenjtalk

mkdir -p /app/pyopenjtalk/build
cp /app/chaquopy/server/pypi/dist/pyopenjtalk/* /app/pyopenjtalk/build/
chmod -R a+r /app/pyopenjtalk/build