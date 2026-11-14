#!/bin/bash
set -e
cd "/c/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"
OUT="../输出文件夹/成片_鸿门宴复刻_480P_v2.mp4"
ffmpeg -y -v error -framerate 24 -start_number 1 -i frames_sub/%04d.png \
  -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -movflags +faststart \
  "$OUT"
echo "encoded: $OUT"
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,nb_frames -of default=noprint_wrappers=1 "$OUT"
