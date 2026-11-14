#!/bin/bash
cd "/c/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹/scripts"
TOTAL=3512
CHUNK=300
START=1
while [ $START -le $TOTAL ]; do
  END=$((START + CHUNK - 1))
  if [ $END -gt $TOTAL ]; then END=$TOTAL; fi
  echo "{\"start\": $START, \"end\": $END}" > ../logs/render_job.json
  echo "=== chunk $START-$END $(date +%H:%M:%S)"
  timeout 700 python -c "import md; md.run_py(r'C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\scripts\f2_render.py', timeout=660)"
  cat ../logs/f2_${START}_${END}.json 2>/dev/null | tr -d '\n'
  echo ""
  START=$((END + 1))
done
echo "ALL DONE $(date +%H:%M:%S)"
