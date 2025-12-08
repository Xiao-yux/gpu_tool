from types import FunctionType
from testclass.testfun import TestFun

class Test:
    name : str = "测试名称"
    runfunc : FunctionType = None
    arg1 = None
    arg2 = None

    @staticmethod
    def test1():
        func = [TestFun.dcgmi_3,TestFun.nccl_test,TestFun.p2pBandwidthLatencyTest,TestFun.fieldiag_level2]
        return func

    @staticmethod
    def test2():
        func = [TestFun.dcgmi_3,TestFun.p2pBandwidthLatencyTest,TestFun.fieldiag_level2]
        return func