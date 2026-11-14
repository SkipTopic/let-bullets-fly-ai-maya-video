import maya.cmds as cmds, json, os
OUT = r'C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹'
d = {'ver': cmds.about(version=1), 'scene': cmds.file(q=True, sn=True)}
json.dump(d, open(os.path.join(OUT, 'logs', '_poller_test.json'), 'w', encoding='utf-8'), ensure_ascii=False)
