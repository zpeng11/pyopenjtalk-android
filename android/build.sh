#!/bin/bash
# build.sh: 更新 meta.yaml 的 version 从 setup.py

set -e  # 退出 on error

source /opt/miniconda3/etc/profile.d/conda.sh
conda activate py310

mkdir -p /app/chaquopy/server/pypi/packages/pyopenjtalk

cd /app/pyopenjtalk

version=$(python setup.py --version | tail -1)
echo "Detected version: $version"
python -c "
import yaml
with open('android/meta.yaml', 'r') as f:
    d = yaml.safe_load(f)
d['package']['version'] = '$version'
with open('/app/chaquopy/server/pypi/packages/pyopenjtalk/meta.yaml', 'w') as f:
    yaml.dump(d, f, default_flow_style=False, indent=2)
print('Updated /app/chaquopy/server/pypi/packages/pyopenjtalk/meta.yaml')
"

cd /app/chaquopy/server/pypi
conda activate py39
./build-wheel.py --python 3.9 --abi armeabi-v7a pyopenjtalk
./build-wheel.py --python 3.9 --abi arm64-v8a pyopenjtalk
./build-wheel.py --python 3.9 --abi x86 pyopenjtalk
./build-wheel.py --python 3.9 --abi x86_64 pyopenjtalk
conda activate py310
./build-wheel.py --python 3.10 --abi armeabi-v7a pyopenjtalk
./build-wheel.py --python 3.10 --abi arm64-v8a pyopenjtalk
./build-wheel.py --python 3.10 --abi x86 pyopenjtalk
./build-wheel.py --python 3.10 --abi x86_64 pyopenjtalk
conda activate py311
./build-wheel.py --python 3.11 --abi armeabi-v7a pyopenjtalk
./build-wheel.py --python 3.11 --abi arm64-v8a pyopenjtalk
./build-wheel.py --python 3.11 --abi x86 pyopenjtalk
./build-wheel.py --python 3.11 --abi x86_64 pyopenjtalk

mkdir -p /app/pyopenjtalk/build
cp /app/chaquopy/server/pypi/dist/pyopenjtalk/* /app/pyopenjtalk/build/
chmod -R a+r+w /app/pyopenjtalk/build