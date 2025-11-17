import os
import json
import hashlib

def update_json(file_path):
    """加载json文件"""
    with open(file_path, 'r', encoding='utf-8') as f:

        data = json.load(f)
    #在[0]位置插入一个新字典
    
    a = os.popen(f"{get_path()}/main --version").read().split('\n')[0]
    print(a)
    ha = os.popen(f"sha256sum {get_path()}/main").read().split(' ')[0]
    data.insert(0, {"version": f"{a}", "url":f"http://192.168.10.20/aisuan","sha256sum":f"{ha}"})
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data
    

        
    

        
def get_path() :
    return os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    path = get_path()
    print(path)
    file_path = os.path.join(path, 'update.json')
    a = update_json(file_path)
    print(a[0])