# FuTransformer：Qwen3-0.6B 数值机制复现

依据：[官方全文§3、§4.8](https://arxiv.org/html/2610.23796v1)。这是首层组件级CPU数值验证，原论文Hopper融合内核尚未复现。

## 实现范围

- 对第一层q_proj执行RMSNorm增益离线折叠、对称INT4、每输出通道×128输入元素静态分组；实际打包2个nibble/byte，FP32 scale。
- GPTQ：4×128 token真实Qwen输入校准，5% damping，FP64 Hessian及误差反馈，无act-order。RTN作为对照。原文32×2048 WikiText-2校准改为代码内4条重复人工文本，是小规模适配，不是标准数据复现。
- 首层KV：RoPE及Q/K norm之后做完整head的归一化Hadamard，KV各每token/head一个amax/7 scale；实际pack/unpack。Q同旋转、attention输出逆旋转。保留BF16主缓存，参考实现每次重新生成INT4镜像；没有增量cache kernel。
- delayed E4M3 FP8实现前一调用amax、零值处理和saturation计数，仅小张量测试，未接入实际Qwen prefill。
- 真实权重矩阵乘为解包后的FP32 reference，输出转BF16；不包含Hopper MMA物理排列、TMA、WGMMA、split-KV和fusion。不能用本代码计时声称论文加速。

## 可复现命令与环境

```sh
python3 demo.py --output results.json
python3 demo.py --test-only --output tests.json
PYTHONPYCACHEPREFIX=/private/tmp/arxiv_20261020_pycache python3 -m py_compile demo.py
```

Python3.9.6、torch2.8.0、transformers4.57.6、CPU4线程、eager attention、BF16主体。使用本地Qwen3-0.6B缓存，revision `c1899de289a04d12100db370d81485cdf75e47ca`，`local_files_only=True`。其他环境用`--model`指定相同快照。校准及两条评估文本完整保存在代码与results.json。

## 本轮实测

完整前向表格使用模拟decode精度的数值参考，并非FuTransformer原生prefill模式。训练和评估都使用重复短文本，不报告标准PPL。

|样例|模式|token NLL|KL(BF16→模式)|top1一致率|
|---|---|---|---|---|
|1|baseline|0.693826|0.000000|1.000000|
|1|rtn|0.691964|0.000581|1.000000|
|1|gptq|0.694624|0.000614|1.000000|
|1|gptq_rotated_kv|0.788998|0.083746|0.960938|
|2|baseline|0.651886|0.000000|1.000000|
|2|rtn|0.655039|0.000550|1.000000|
|2|gptq|0.651571|0.000406|1.000000|
|2|gptq_rotated_kv|0.699307|0.068204|0.976562|

本次加载、校准、评估及缓存smoke test总耗时22.739秒，不是kernel延迟。两条样例另外执行64-token **BF16 prefill** 后8次单token INT4参考decode，最终Cache长度72、logits全部有限。

第一层q_proj原BF16为4,194,304bytes，INT4 payload1,048,576bytes+scale65,536bytes，合计1,114,112bytes，矩阵约3.765倍压缩。实验同时保留原层和反量化临时矩阵，不能据此推导进程内存下降。最后一条cache实例，BF16主副本294,912bytes，INT4镜像payload73,728+scale4,608bytes；共存总373,248bytes，约为原主副本的1.266倍，下降的是decode可读取的镜像数据量。

8项测试通过：全nibble往返、Hadamard逆变换、QK内积保持、零cache、GPTQ分组与packing、gain折叠等价、FP8零值与饱和、单位Hessian的GPTQ=RTN；语法与导入通过。结果显示此小样本中GPTQ未在所有样例优于RTN，KV量化增大KL，不能用其声称整模无损。

## 未完成项

没有H100/Hopper环境，未编写或验证原文CUDA融合kernel/MMA布局；未做全模型INT4、标准WikiText-2、多种子、任务准确率或吞吐评估。当前工作完成论文核心数值机制及Qwen实际运行的有限验证，完整系统复现仍未完成。
