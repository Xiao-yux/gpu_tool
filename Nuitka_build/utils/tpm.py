from noneprompt import CancelledError, ListPrompt, Choice, InputPrompt,CheckboxPrompt
import asyncio

async def tpm():
    choices: list[Choice] = []
    choices.append(Choice("系统信息", "1"))
    choices.append(Choice("FD压测", "2"))
    choices.append(Choice("GPUburn压测", "3"))
    choices.append(Choice("Dcgmi测试", "4"))
    
    print(choices[0])
    while True:
        choice = await ListPrompt("请选择要进行的操作：",choices,validator=lambda choice: choice != choices[0] ).prompt_async()
        print (choice)
if __name__ == '__main__':
    
    try:
        asyncio.run(tpm())
        print("操作完成")
    except CancelledError:
        print("用户取消了操作")