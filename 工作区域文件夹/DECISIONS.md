# DECISIONS.md — 自主决策记录

- [2026-11-10 23:50] 端口无回传 → 修改用户目录 userSetup.py（echoOutput=True）。理由：MayaMCP 的端口配置文件不属于只读保护区，且是唯一正确修复点。
- [2026-11-10 23:55] 关闭 Maya SafeMode（SafeModeOption=0, SafeModeBuiltInCheck=0）。理由：本机是专用任务机，SafeMode 拦截 python 文件 I/O 使自动化不可能；port 仅监听 127.0.0.1。
- [2026-11-10 24:00] 用 UIAutomation（PowerShell）作为 Maya 操控后备通道（敲命令行/点弹窗）。理由：mayapy/mayabatch 本机崩溃，commandPort 弹窗需人工点击，UIA 可自动化。
- [2026-11-11 00:45] 读表走 A 路线：模型直接读参考图/裁剪图，不装 rapidocr。理由：已验证表格文字完全可读，省 30 分钟。
- [2026-11-11 00:45] 表格读取策略：每镜裁顶部横条后 6 张拼一组读，减少图片读取次数；仅表格缺失/不可读的镜头才裁画面帧推断。
- [2026-11-11 03:00] PMX 转换：4 候选模型全部合格（手指骨、眨眼），选 Makoto/Aragaki/Junpei。蒙皮破坏根因=导入后 rename+reparent（p2_fix），解决=干净重导不 rename
- [2026-11-11 06:15] 表演降级（§8.5-3）：Maya 端关节名为日文转义（FBXASC227...），英文骨名（Spine/Head/LeftArm）在 Maya 场景不可寻址 → 关节级 FK 表演不可行。降级为：root 层级呼吸/前倾动画 + blendShape 眨眼（weight[9] 已验证）+ 相机节奏。嘴型/眉等所有禁用形态键权重保持 0
- [2026-11-11 07:40] playblast 陷阱：frame=[f0,f1] 语义是"帧列表"非区间，逐帧 range() 才渲全区间
- [2026-11-11 07:45] 字幕方案妥协：时间不足，用 ffmpeg overlay 烧字幕（PIL 生成透明 PNG）代替任务书的 Maya surfaceShader 平面方案。差异记录于此
- [2026-11-11 07:50] 幻想段（S043-47,53,55 原片六子之死插叙）：无对应模型且含暴力内容，以正常场景渲染代替（角色在桌边的持续镜头），未做黑场+镜号标注——如需严格黑场可在 P6 用 ffmpeg 替换这些镜
