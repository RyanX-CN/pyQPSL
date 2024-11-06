# build_exe.py
import PyInstaller.__main__

PyInstaller.__main__.run([
    'Main.py',  # 你的主脚本文件
    '--onefile',  # 打包成一个单独的可执行文件
    '--name=pyQPSL',  # 可执行文件的名称
    '--distpath=D:/output/dist',  # 指定输出目录
    '--workpath=D:/output/build',  # 指定临时工作目录
])