import os
# 当前项目路径
projectPath = os.path.split(os.path.abspath(__file__))[0]
if __name__ == "__main__":
    print(projectPath)
