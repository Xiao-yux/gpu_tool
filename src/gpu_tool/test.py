from gpu_tool.i18n.i18n import init_i18n
from gpu_tool.utils.tool import Tools

def main():
    i18n = init_i18n()
    print(f"{Tools.get_dist_path()}/i18n/locales/{i18n.lang}.json")

if __name__ == '__main__':
    main()
