# 2609.05334：Qwen3-0.6B 上的真实组件迁移

论文：[官方v1全文](https://arxiv.org/html/2609.05334v1)。原研究是农业图像上的 ViT-B/16 → TinyViT → INT8；此目录以 **真实 Qwen3-0.6B checkpoint** 验证可迁移组件，不声称重现原视觉实验。`full_paper_reproduction=false`。

## 已执行的代码与边界

| 组件 | 具体实现 | 本次实际运行及与论文差异 |
|---|---|---|
| 动态INT8 PTQ | PyTorch `quantize_dynamic`，全部`nn.Linear`，QINT8，qnnpack；默认MinMax权重observer，逐张量对称标定、存储qscheme为per_tensor_affine且zero point=0 | 完整28层Qwen的197个Linear，包括Q/K/V/O、SwiGLU三投影与lm_head；不是只量化一块小张量 |
| 校准/激活 | 动态PTQ无离线激活校准；输入输出API为FP32，后端在调用时量化激活 | 不把它混称Core ML权重INT8解量化浮点GEMM；不复现论文的静态PTQ对照（1,000张类均衡图像不可用） |
| H-BAC | 真实因果CE的Hessian-vector product，注意力/MLP分别K=10个Rademacher探针；算法1的max(C,0)、直接sqrt权重、双裁剪 | 只对Qwen第0、14块计算，1段最多16token的本地校准文本；全28块可通过`--blocks`指定，但本次未执行 |
| 结构掩码 | Taylor `abs(w*grad)`，GQA组包含2个Q头及对应K/V头和O列；SwiGLU对应gate/up行、down列 | Qwen 16Q:8KV不同于ViT独立头；保留至少1组，未物理缩形，因此不声称剪枝产生体积/内核收益 |
| 恢复与KD | 1次真实掩码CE恢复；冻结剪后教师，4层学生取教师0/9/18/27层，均头注意力MSE+因果CE+T²KL；0.5/0.3/0.2，T=4 | 真实反向传播及AdamW一步，替代论文一轮恢复与15轮视觉KD；学生embedding/最后norm冻结，其余块训练。不是伪标签或空壳 |
| 学生量化 | 蒸馏后4层Qwen学生全部29个Linear做native INT8并完整前向 | 学生架构非论文TinyViT，不计作完整Qwen0.6B的压缩质量结论 |

论文未明确MLP平衡λ、observer、具体粒度及后端。本实现明确选择λ=1、PyTorch默认动态权重observer、qnnpack；这些是迁移设置，不能称为作者精确配置。论文负曲率处理的文字“绝对值”与算法1不同，本实现选择算法1的非负截断。其第二次裁剪也可能改变全局均值，代码不声称总预算总是精确保持。

## 环境与命令

实际环境：macOS 26.6.2 arm64，Python3.9.6，PyTorch2.8.0，Transformers4.57.6，CPU4线程，随机种子42。Qwen本地缓存revision：`c1899de289a04d12100db370d81485cdf75e47ca`。不下载权重；缺缓存直接失败，不用随机模型冒充Qwen。极小随机Qwen仅用于单元验证GQA掩码。

在此目录运行：

```bash
python3 demo.py --mode ptq --output results_ptq.json
python3 demo.py --mode components --output results_components.json
PYTHONPYCACHEPREFIX=/private/tmp/arxiv_20260908/pycache python3 -m py_compile demo.py
```

两种模式均先执行四项检查：Hutchinson对已知二次函数trace精确为6、直接预算分配/零曲率回退、GQA/SwiGLU掩码对应关系、native INT8真实执行。均通过；导入、语法、完整前向及训练步骤也通过。系统默认Python编译缓存目录最初不可写，指定临时缓存后语法检查通过。

校准文本与独立评估文本原样记录在JSON/代码中。PTQ模式不使用所列校准文本，仅components模式使用；它们是算法健全性样本，不是WikiText/C4质量基准。`--seq-len 16`是上限，不意味着所有文本都恰有16个token。

## 实际结果

原始结果：[完整Qwen PTQ](results_ptq.json)、[H-BAC/KD组件](results_components.json)。

| 完整Qwen3-0.6B检查 | FP32 | 动态INT8 |
|---|---:|---:|
| 独立短文本next-token CE | 6.347614 | 7.014916 |
| 单次前向秒数 | 0.497746 | 0.916741 |
| 逻辑张量payload | 2,384,199,680字节 | 估计1,218,579,536字节 |

相对logits L2误差 **0.352920**，top-1一致率 **0.272727**。估计张量payload比约 **1.9565倍**：embedding仍FP32，原先与embedding共享的lm_head在量化后变成独立INT8表示，所以不能按所有模型权重简单声称4倍。估计排除打包内核、序列化及分配器开销，不是实测checkpoint文件大小。

单次前向没有预热/重复统计，不能作为速度基准；实际观测也没有加速。qnnpack提示忽略`reduce_range`，保留这一后端限制，不能将结果当作任意INT8实现的质量结论。

H-BAC的块曲率分别为 **5712.380 / 567.933**，分配比例 **0.760276 / 0.239724**。实际删除GQA组 **7/8、2/8**，MLP单元 **2336/3072、737/3072**；离散组取整后不能把比例当精确参数稀疏率。剪枝后校准CE为15.99615，说明此激进迁移具有明显损害。

4层学生在独立评估文本上的CE经一次KD从 **15.730988→15.584406**，再量化为 **16.156311**；KD训练损失由真实CE15.381315、注意力MSE0.017295、温度KL10.946679组成，总损失9.885181。仅一次更新后的轻微下降不证明收敛，也不证明蒸馏优于同预算直接训练。

## 未完成的原论文复现

没有农业原始数据/已训练ViT与TinyViT checkpoint，未建立跨村庄/跨手机OOD分割，未执行15轮视觉蒸馏、完整剪枝预算扫描、静态PTQ、结构缩形、Core ML导出或手机基准。Qwen采用GQA、SwiGLU和因果语言目标，与原ViT不等价。

本目录提供可运行算法、真实权重运行和明确负面结果；**不复现论文95.13%视觉准确率、54.5倍文件压缩或其延迟数字**。后续优先做代表性语言校准集与同深度直接训练对照，再增加步骤、预算和实际打包存储/延迟评估。
