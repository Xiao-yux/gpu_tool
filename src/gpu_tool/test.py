from i18n.i18n import init_i18n
from utils.tool import Tools

def main():
    i18n = init_i18n()
    print(f"{Tools.get_dist_path()}/i18n/locales/{i18n.lang}.json")

if __name__ == '__main__':
    print(Tools.__name__)
