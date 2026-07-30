
### 通用量化（48 篇）

1. **2603.01399** Quasar: Quantized Self-Speculative Acceleration for Rapid Inference via Memory-Efficient Verification
   → Quasar 指出自投机/前瞻解码把瓶颈转移到验证阶段（全精度前向受显存带宽限制），提出免训练框架——**专对验证阶段用低比特量化**减半显存流量；实证显示激进结构剪枝损害验证精度而量化验证能高保真保留 logit 分布，在 OpenPangu 与 Qwen3 上保持与全精度相当的接受长度并实现 1.28× 端到端吞吐提升。

2. **2603.01599** Boosting Entropy with Bell Box Quantization
   → BBQ 提出"量化器输出不必与输入同域"的核心洞察，在输入域做信息论最优（ITO）量化、在输出域映射回计算高效的整数类型，在不牺牲计算效率的前提下，使 4/3/2/1-bit 模型的困惑度分别较此前 SOTA QAPT 方法最多降低 2/4/5/18 个点（ICLR 2026 录用）。

3. **2603.01776** FreeAct: Freeing Activations for LLM Quantization
   → FreeAct 打破变换类量化方法的"静态一对一变换"约束，利用激活的秩亏特性把激活变换与权重变换解耦，为不同 token 类型（视觉/文本、掩码 token）分配各自的激活变换矩阵、权重侧保持统一静态变换，在 dLLM 与 MLLM 上较基线最高提升 5.3%。

4. **2603.02170** SageBwd: A Trainable Low-bit Attention
   → SageBwd 把 SageAttention 从推理扩展到训练——对 7 个注意力矩阵乘中的 6 个做 INT8 量化；本工作诊断出预训练差距的根源（反向分数梯度 dS 的量化误差），并给出四条结论：大 token 步长下 QK-norm 必不可少、降低 tokens/step 可使 SageBwd 在预训练中追平全精度注意力、K-smoothing 关键而 Q-smoothing 收益有限。

5. **2603.02731** Practical FP4 Training for Large-Scale MoE Models on Hopper GPUs
   → 本文面向 Hopper GPU 提出大规模 MoE 模型的实用 FP4 训练方案，解决 MoE 架构在低比特训练下的独有挑战，使 FP4 训练在超大规模稀疏模型上可行且高效。

6. **2603.02883** SemanticDialect: Semantic-Aware Mixed-Format Quantization for Video Diffusion Transformers
   → SemanticDialect 把块级混合格式量化推进到"语义感知"层面——每个块从扩充了查找表的格式簿（formatbook）中选择最优格式（dialect），配合注意力引导的激活分解（残差量化）与语义感知方言分配（SeDA，强制语义相关 token 格式统一），在 Open-Sora 2.0 上超越 MXFP4/NVFP4 等此前方法并逼近 FP16 质量，且通过 RTL 设计与 GPU kernel 验证了硬件可部署性。

7. **2603.03380** LiteVLA-Edge: Quantized On-Device Multimodal Control for Embedded Robotics
   → LiteVLA-Edge 在 Jetson Orin 级硬件上实现完全端侧 VLA 推理——FP32 监督图像到动作微调 + 后训练 4-bit GGUF 量化 + llama.cpp GPU 加速推理，在 ROS 2 集成的感知-推理-动作管线中实现 150.5 ms 平均端到端延迟（约 6.6 Hz），全程离线运行。

8. **2603.04162** Bielik-Q2-Sharp: A Comparative Study of Extreme 2-bit Quantization Methods for a Polish 11B Language Model
   → Bielik-Q2-Sharp 是首个针对波兰语 LLM 的 2-bit 量化系统评测——以 Bielik-11B-v2.3-Instruct（Mistral 架构）为基座，在波兰语语料（CulturaX-PL）与共享 Hessian 下对比 QuIP#/SpinQuant+GPTQ/ButterflyQuant/QTIP/VPTQ/AQLM 六种方法，最优变体 QuIP# E8P12 在 22 个波兰语基准上达 71.92%（与 IQ2_XXS 的 72.07% 处于统计噪声内），并发现旋转类方法"保对数似然但生成崩溃"的 MC-生成解离现象。

9. **2603.04308** Activation Outliers in Transformer Quantization: Reproduction, Statistical Analysis, and Deployment Tradeoffs
   → 本文在 BERT-base/QNLI 上复现并扩展了 Bondarenko 等（EMNLP 2021）的激活异常值现象——全局 W8A8 使验证精度从 89.66% 暴跌至 54.33%（-35.33 点），末层峰度达 271、55% 激活能量集中于 1% 通道；混合精度 PTQ 恢复至 89.42%，而 99.0–99.99 分位裁剪完全无效（~50.54%），证明大激活通道编码的是结构化信号而非噪声，必须用通道感知精度分配。

10. **2603.04359** Dissecting Quantization Error: A Concentration-Alignment Perspective
   → 本文用信号量化噪声比（SQNR）分解线性层量化误差，证明固定比特下 SQNR 由**权重/激活的集中度**（离散度与异常值）与**主导变化方向的对齐度**两因子决定；据此提出块 Concentration-Alignment Transform（CAT），用小校准集协方差同时改善集中度与对齐度、近似最大化 SQNR，在多个 LLM 上 4-bit 精度持续匹配或超越此前变换类量化方法。

11. **2603.04800** MASQuant: Modality-Aware Smoothing Quantization for Multimodal Large Language Models
   → MASQuant 以 SmoothQuant 为案例剖析其用于 MLLM 的两大问题——平滑失配（Smoothing Misalignment）与跨模态计算不变性失效，提出模态感知平滑（MAS，学习模态特异平滑因子）与跨模态补偿（CMC，用 SVD 白化把多模态激活差异变为低秩形式），在双模态与三模态 MLLM 上均获稳定量化性能，跻身 SOTA PTQ 之列。

12. **2603.04956** WaterSIC: Information-Theoretically (Near) Optimal Linear Layer Quantization
   → 本文从信息论角度分析稠密线性层转低精度时"压缩长度-输出偏差"的权衡，证明流行的 GPTQ 与信息论极限的差距可任意大；提出 WaterSIC——模仿经典"注水（waterfilling）"解法为权重矩阵不同列分配不同量化码率，对所有输入激活协方差矩阵一致地把码率差距控制在 0.255 bit 内，在 Llama 与 Qwen 家族上 1–4 bit 全部码率刷新 SOTA。

13. **2603.05168** Sparse-BitNet: 1.58-bit LLMs are Naturally Friendly to Semi-Structured Sparsity
   → Sparse-BitNet 首次把 1.58-bit 量化与动态 N:M 稀疏统一到一个稳定训练框架，发现 1.58-bit BitNet 天然比全精度模型更兼容 N:M 稀疏——同稀疏度下退化更小、崩溃前可容忍更高结构稀疏；配合自研稀疏张量核，训练与推理最高加速 1.30×。

14. **2603.05232** SlideSparse: Fast and Flexible (2N-2):2N Structured Sparsity
   → SlideSparse 的滑动窗口分解把任意 (2N-2):2N 权重块无损重构为 N-1 个重叠的 2:4 兼容窗口，Activation Lifting 把激活重排融合进逐 token 量化（近零成本），使 6:8（25% 剪枝）等温和稀疏首次在商用 GPU 上获得稀疏张量核加速；Qwen2.5-7B 在 6:8 下实测 1.33× 加速，逼近理论上限 N/(N-1)=4/3。

15. **2603.06746** ButterflyViT: 354$\times$ Expert Compression for Edge Vision Transformers
   → ButterflyViT 不再把专家当作独立权重矩阵，而是把专家视为**统一共享量化基底的几何重定向**——对共享三值原型施加学习旋转生成多样专家，使显存从 O(N_E·d²) 降为关于专家数亚线性；配合空间平滑正则化（惩罚相邻 patch 路由不规则），在 CIFAR-100 上 64 专家实现 354× 显存削减且精度损失可忽略。

16. **2603.07904** DyQ-VLA: Temporal-Dynamic-Aware Quantization for Embodied Vision-Language-Action Models
   → DyQ-VLA 针对 VLA 模型静态量化的两大挑战——时序动态敏感性（固定精度忽视各阶段误差容忍度差异）与实时分配难，提出敏感性感知的比特切换策略（用实时运动学代理触发切换）+ 运动学引导的动态比特分配模块；仅需原模型 30.9% 的显存即保持性能。

17. **2603.08173** Evolution Strategy-Based Calibration for Low-Bit Quantization of Speech Models
   → ESC 发现音频激活的校准范围大导致标准校准信息损失严重，把激活缩放建模为优化问题并用"两步局部-全局"进化策略求解；实现全 INT8 量化性能无损，并成为首个在多语音任务上全 INT4 量化近无损的校准方法，可与 PTQ 方法集成。

18. **2603.08185** SERQ: Saliency-Aware Low-Rank Error Reconstruction for LLM Quantization
   → SERQ 用**单个低秩补偿矩阵**（而非两个顺序因子）做误差重建，通过静态激活平坦化、显著性感知误差重建、离线权重置换三阶段联合缓解激活与权重显著性引起的量化误差，在 W4A8 与 W4A4 下均优于此前误差重建方法，且比最先进的旋转类 W4A4 方法精度更高、校准复杂度大幅降低。

19. **2603.08747** Diagnosing FP4 inference: a layer-wise and block-wise sensitivity analysis of NVFP4 and MXFP4
   → 本文对 NVFP4 与 MXFP4 两种主流 FP4 微缩放格式做了逐层、逐块的敏感度分析，系统诊断 FP4 推理中哪些层、哪些块最易受量化损伤，为 FP4 部署提供可操作的诊断依据与格式选择指导。

20. **2603.09582** BinaryAttention: One-Bit QK-Attention for Vision and Diffusion Transformers
   → BinaryAttention 理论论证"二值化注意力保留本质相似性关系"，仅保留 Q/K 符号、用位运算替代浮点点积，配合可学习偏置、量化感知训练与自蒸馏，在 A100 上比 FlashAttention2 快 2 倍以上，且在 ViT 与 DiT 基准上匹配甚至超过全精度注意力。

21. **2603.10444** The Curse and Blessing of Mean Bias in FP4-Quantized LLM Training
   → 本文系统分析 FP4 量化 LLM 训练中"均值偏置（mean bias）"现象的双重作用——它既是损伤训练稳定性的"诅咒"，在特定条件下又能被利用为"祝福"，为设计更稳定的 FP4 训练方案提供了机理层面的认识。

22. **2603.11021** Leech Lattice Vector Quantization for Efficient LLM Compression
   → 本文把 24 维 Leech 格（已知最高维的最优球堆积/亲吻构型）引入 LLM 量化，扩展基于扩展 Golay 码构造的搜索算法以支持索引（免码本存储的比特串转换）、Leech 格壳并集上的角度搜索等，使高维格向量量化可用于 LLM 压缩，突破标量量化的信息论极限。

23. **2603.13765** Knowledge Distillation for Large Language Models
   → 本文用 Qwen 3B（教师）蒸馏 Qwen 0.5B（学生），在英语/西班牙语 Dolly-15k 与代码 BugNet/PyTorrent 数据集上蒸馏，学生保留教师 70%–91%（英语）、最高 95%（西班牙语）、最高 93.5% Rouge-L（代码）的能力；代码任务上结合 CoT 提示与 GRPO（CoT 标注 Codeforces 数据）进一步提升推理连贯性与正确率，训练后 4-bit 权重量化进一步降低显存与延迟。

24. **2603.13931** True 4-Bit Quantized Convolutional Neural Network Training on CPU: Achieving Full-Precision Parity
   → 本文提出 tanh 软权重裁剪 + 对称量化 + 逐层动态缩放 + 直通估计器的组合，在普通 CPU（Google Colab 免费档）上从零训练 3.25M 参数 VGG 网络，CIFAR-10 达 92.34%（距全精度 92.5% 仅 0.16%），CIFAR-100 达 70.94%，每层仅 15 个唯一权重值、8× 显存压缩，并在 OnePlus 9R 手机 6 epoch 内达 83.16%。

25. **2603.14062** TMPDiff: Temporal Mixed-Precision for Diffusion Models
   → TMPDiff 打破"所有去噪步用同一精度"的惯例，提出按时间步分配不同数值精度的框架；基于"量化误差随时间步加性累积"的假设（已实验验证），设计线性复杂度的自适应二分分配算法，在 4 个 SOTA 扩散模型、3 个数据集上相同加速比下感知质量提升 10–20%，FLUX.1-dev 上以 2.5× 加速达到全精度 90% 的 SSIM。

26. **2603.16590** BATQuant: Outlier-resilient MXFP4 Quantization via Learnable Block-wise Optimization
   → BATQuant 指出为整数格式设计的全局正交旋转与 MXFP4 存在根本性格式失配（旋转把异常值能量跨量化块转移、并制造双峰分布），于是把变换限制到与 MXFP 粒度对齐、放松正交约束做分布整形，配合全局-私有 Kronecker 分解与块级可学习裁剪，在激进 W4A4KV16 下恢复多模态基准 96.43% 的全精度性能，刷新 SOTA。

27. **2603.16731** Understanding Quantization of Optimizer States in LLM Pre-training: Dynamics of State Staleness and Effectiveness of State Resets
   → 本文研究低精度 EMA 优化器状态，揭示量化使许多名义更新舍入回原值、状态"停滞"而减慢适应；建立单步停滞概率的预测模型刻画停滞随时间累积，并给出机理解释——为何重置优化器状态在低精度下有效（重置可暂时恢复响应性），据此推导理论指导的改进方法。

28. **2603.17230** KANtize: Exploring Low-bit Quantization of Kolmogorov-Arnold Networks for Efficient Inference
   → KANtize 系统研究低比特量化对 KAN 的影响——KAN 用可学习 B 样条激活（系数为可学习参数），推理时样条求值增加计算复杂度；本文考察 8-bit 以下量化对 KAN 精度与计算复杂度的影响，填补 KAN 量化研究的空白。

29. **2603.17354** Beyond Outliers: A Data-Free Layer-wise Mixed-Precision Quantization Approach Driven by Numerical and Structural Dual-Sensitivity
   → NSDS 指出现有逐层混合精度量化（LMPQ）把层内所有权重模块同质化、且只用单一数值属性估计敏感度，于是把每层机理分解为不同操作角色、从数值与结构双视角量化敏感度，再用 MAD-Sigmoid 与 Soft-OR 鲁棒聚合为统一层级指标指导比特分配；在多种模型与下游任务上免校准地持续优于各基线。

30. **2603.17891** RAMP: Reinforcement Adaptive Mixed Precision Quantization for Efficient On Device LLM Inference
   → RAMP 用离策略 Soft Actor-Critic 学习逐层比特分配以在全局比特预算下最小化困惑度，策略以 11 维激活/权重/结构统计嵌入为条件实现零样本跨模型迁移；配合 Scale Folding 预处理把激活异常值迁入权重，在 Llama 2 7B 上以 3.65 有效比特达 5.54 PPL，优于均匀 4-bit AWQ（5.60）与 GPTQ，且仅在 Llama 2 7B 上训练的策略可零样本迁移到 Llama 2 13B 与 Mistral 7B。

31. **2603.18095** Q-Drift: Quantization-Aware Drift Correction for Diffusion Model Sampling
   → Q-Drift 把量化误差视为每个去噪步上的隐式随机扰动，推导出保持边缘分布的漂移校正，仅需 5 组配对的全精度/量化校准运行估计逐步方差统计，即插即用于常见采样器与 PTQ 方法；在 6 个文生图模型、3 种采样器、2 种 PTQ 方法上多数场景改善 FID，PixArt-Sigma（SVDQuant W3A4）最高降低 4.59 FID 且 CLIP 分数不变。

32. **2603.18423** SynQ: Accurate Zero-shot Quantization by Synthesis-aware Fine-tuning
   → SynQ 针对零样本量化的三大障碍——合成数据噪声、基于偏离目标模式的预测、错误硬标签误导——提出低通滤波去噪、类激活图对齐预训练模型、困难样本仅用软标签三招，取得超越现有 ZSQ 方法的 SOTA 精度。

33. **2603.18426** Prune-then-Quantize or Quantize-then-Prune? Understanding the Impact of Compression Order in Joint Model Compression
   → 本文首次系统研究"先剪枝后量化"还是"先量化后剪枝"的顺序问题，形式化压缩顺序优化并提出**渐进强度假说**（较弱扰动应先于较强扰动），给出理论保证——一种顺序的相对收益随底层性能差距增大而增大；在语言与视觉模型上验证假说，并推广到多阶段压缩与混合精度量化。

34. **2603.18742** 6Bit-Diffusion: Inference-Time Mixed-Precision Quantization for Video Diffusion Models
   → 6Bit-Diffusion 发现"块的输入-输出差异"与其内部线性层量化敏感度强线性相关，据此设计轻量预测器动态分配 NVFP4（时序稳定层）与 INT8（易变层），并利用块残差的时序一致性提出 Temporal Delta Cache 跳过不变块计算，实现 1.92× 端到端加速与 3.32× 显存削减，刷新视频 DiT 高效推理基线。

35. **2603.19172** DyMoE: Dynamic Expert Orchestration with Mixed-Precision Quantization for Efficient MoE Inference on Edge
   → DyMoE 基于"专家重要性高度倾斜且随深度变化"的观察，提出重要性感知动态量化、深度自适应调度、前瞻预取三件套，在商业边缘硬件上使 TTFT 降低 3.44×–22.7×、TPOT 最高加速 14.58×（相对 SOTA offloading 基线），实现边缘设备上实时且保精度的 MoE 推理。

36. **2603.19296** TTQ: Activation-Aware Test-Time Quantization to Accelerate LLM Inference On The Fly
   → TTQ 把量化校准从离线搬到测试时——通过高效的在线校准，使激活感知量化能适配每一个 prompt、无论下游任务是否见过，在免重训练压缩的同时解决校准数据的域偏移问题，并取得超越 SOTA 基线的量化性能与推理加速。

37. **2603.22324** DAQ: Delta-Aware Quantization for Post-Training LLM Weight Compression
   → DAQ 指出标准重建式量化目标与基座模型无关，会让量化噪声不成比例地破坏编码后训练行为的小幅度参数增量 ΔW；它用"符号保持率 + 余弦相似度"两个 delta 感知指标直接优化 ΔW 的方向保真，仅需基座与后训练权重矩阵，在 FP8 试点实验中恢复了标准量化丢失的风格特异能力、同时保持通用性能。

38. **2603.22370** FAAR: Format-Aware Adaptive Rounding for NVFP4
   → FAAR 指出传统舍入策略忽视 NVFP4 数值网格的非均匀性导致次优舍入，提出把非均匀网格显式纳入优化、由损失梯度自适应调整舍入决策的可学习舍入方法，逼近理论最优量化，专为边缘设备超低比特 LLM 部署设计。

39. **2603.22943** PersonalQ: Select, Quantize, and Serve Personalized Diffusion Models for Efficient Inference
   → PersonalQ 用检查点的"触发 token"作为共享信号，把检查点选择（意图对齐混合检索 + LLM 重排 + 必要时澄清提问 + 重写提示词）与量化（保护个性化概念脆弱表示的触发器感知量化）连接起来，解决个性化文生图模型仓库高效服务中"请求误路由"与"标准 PTQ 扭曲个性化表示"两大难题。

40. **2603.23575** APreQEL: Adaptive Mixed Precision Quantization For Edge LLMs
   → APreQEL 通过分析逐层贡献并推断不同量化类型在目标硬件上的行为，在内存、延迟、精度的用户自定义优先级下为每层分配最合适的量化类型，解锁了均匀量化无法达到的配置设计空间，高效支撑边缘设备上的 LLM 部署。

41. **2603.25284** SliderQuant: Accurate Post-Training Quantization for LLMs
   → SliderQuant 发现 LLM 浅层/深层比中间层对量化更敏感、且首/末层最敏感，提出层间滑动量化（三种滑动窗口设计）+ 层内增量滑动量化的两级框架，仅用少量可学习参数即可跨层降低量化误差，在 Llama/Llama2/Llama3/Qwen2.5、DeepSeek-R1 蒸馏模型与大型 MoE 上超越包括旋转变换类最新 PTQ 在内的现有方法（ICLR 2026 录用，代码开源）。

42. **2603.25385** GlowQ: Group-Shared LOw-Rank Approximation for Quantized LLMs
   → GlowQ 针对低秩校正方法（LQER/QERA/ASER）在每层都插入校正模块带来的延迟与显存开销，提出在每个输入共享组只缓存一个共享右因子、只恢复收益最高的组/层，使 TTFB 平均降低 5.6%、吞吐提升 9.6%、WikiText-2 PPL 降低 0.17%；其选择性变体 GlowQ-S 进一步将 TTFB 降 23.4%、吞吐提升 37.4%，精度损失控制在平均 0.2 个百分点内。

43. **2603.27914** ITQ3_S: High-Fidelity 3-bit LLM Inference via Interleaved Ternary Quantization with Rotation-Domain Smoothing
   → ITQ3_S 先用快速 Walsh-Hadamard 变换（FWHT）把权重预旋转为近似高斯分布，再做均匀三值编码，并将 256 点逆 FWHT 融合进 CUDA 共享内存加载阶段，使重构误差仅由三值网格决定；在 RTX 5090 上达到与 FP16 竞争的困惑度，吞吐超过 4-bit 方案的 1.5 倍。

44. **2603.28845** OneComp: One-Line Revolution for Generative AI Model Compression
   → OneComp 把碎片化的量化算法、精度预算、校准策略与硬件执行细节整合为一个可复现、资源自适应的管线——给定模型标识与可用硬件，自动检查模型、规划混合精度分配、执行从逐层压缩到块级精炼再到全局精炼的渐进量化；首个量化检查点即可部署，后续阶段持续提升同一模型质量。

45. **2603.29078** PolarQuant: Optimal Gaussian Weight Quantization via Hadamard Rotation for LLM Compression
   → PolarQuant 通过"块级归一化到单位超球面 → Walsh-Hadamard 旋转 → 匹配高斯分布质心量化"三阶段，使 Qwen3.5-9B 的 absmax Q5 困惑度从 6.90 降至 6.40（距 FP16 仅 +0.03），消融显示 Hadamard 旋转贡献 98% 的改进，且无需任何校准数据；作为 INT4 预处理还能把 absmax INT4 的 PPL 从 6.68 降到 6.56。

46. **2603.29535** Quantization with Unified Adaptive Distillation to enable multi-LoRA based one-for-all Generative Vision Models on edge
   → QUAD 把 LoRA 权重当作运行时输入（而非编译进模型图），实现单一共享模型动态切换多任务、无需重编译；再通过量化感知训练把多个 LoRA 对齐到共享量化配置，在多种移动芯片上实现最高 6× 显存削减与 4× 延迟改善，同时保持多 GenAI 任务的高视觉质量。

47. **2603.29768** Big2Small: A Unifying Neural Network Framework for Model Compression
   → 本文用测度论构建模型压缩的统一数学框架，证明每种压缩技术在数学上等价于一个带正则化的神经网络；据此提出免数据压缩框架 Big2Small——把隐式神经表示（INR）从数据域迁移到网络参数域，训练紧凑 INR 编码大模型权重并在推理时重构，配合 Outlier-Aware 预处理与 Frequency-Aware 损失，在图像分类与分割上取得与 SOTA 相当的精度和压缩比。

48. **2604.03298** ENEC: A Lossless AI Model Compression Method Enabling Fast Inference on Ascend NPUs
   → ENEC 针对昇腾 NPU 上权重数据传输瓶颈与现有无损压缩算法移植后吞吐极低的问题，提出专为 AI 模型权重定制、为昇腾 NPU 优化的无损压缩方法——采用块级定长编码方案，在保持模型精度的同时实现快速推理。


### KV Cache 量化（6 篇）

49. **2603.14224** Self-Indexing KVCache: Predicting Sparse Attention from Compressed Keys
   → 本文提出把压缩后的 key 表示不仅当存储、更当**自索引结构**直接支持稀疏注意力——设计基于符号的 1-bit 向量量化方案，把压缩与检索统一在单一硬件友好格式中，消除外部索引与学习式预测器的需求，为显存受限推理提供轻量鲁棒的方案。

50. **2603.16435** VQKV: High-Fidelity and High-Ratio Cache Compression via Vector-Quantization
   → VQKV 首次把向量量化（VQ）引入免训练 KV cache 压缩，用少量整数索引表示数千浮点值，同时实现高压缩率与高重构保真；在 LLaMA3.1-8B 上达 82.8% 压缩率、LongBench 保留基线 98.6% 性能、同显存下生成长度延长 4.3×。

51. **2603.27467** TurboAngle: Near-Lossless KV Cache Compression via Uniform Angle Quantization
   → TurboAngle 在 FWHT 域量化角度——随机对角旋转使相邻元素对在单位圆上近似均匀分布，再配合逐层 early-boost（每层独立配置 K/V 码本大小、给关键层更高精度），在 7 个 1B–7B 模型上 6 个达近无损（4 个无损）、每元素仅 3.28–3.67 角度比特；配合非对称范数量化（K 8-bit、V 4-bit 对数域），Mistral-7B 总 6.56 bit/元素、PPL 仅退化 +0.0014 且免校准。

52. **2603.27469** KV Cache Quantization for Self-Forcing Video Generation: A 33-Method Empirical Study
   → 本文在 Wan2.1 Self-Forcing 堆栈上系统评测 33 种量化与缓存策略变体（610 个 prompt 级观测、63 个基准级摘要），发现：FlowCache 启发的软剪枝 INT4 变体是最强实用区（5.42–5.49× 压缩、峰值显存从 19.28 GB 降至约 11.7 GB）；最高保真方法（PRQ_INT4、QUAROT_KV_INT4）因运行时/显存代价并非最佳部署选择；且"名义压缩"不等于显存下降——注意力与刷新阶段的 BF16 缓冲会抵消收益。

53. **2603.27819** KVSculpt: KV Cache Compression as Distillation
   → KVSculpt 跳出"选择或合并原始 KV 对"的范式，直接在连续嵌入空间**优化一组不受约束的更小 KV 对**以保留每层注意力行为——key 用 L-BFGS 优化、value 用最小二乘闭式求解交替进行；配合基于 pilot 运行的自适应预算分配（按层/头难度重分配压缩预算），在 Qwen2.5-1.5B、2048 token 上下文下，KL 散度较 Select+Fit 降低 3.5–4.1×，自适应分配再降 1.3×。

54. **2603.28430** IsoQuant: Hardware-Aligned SO(4) Isoclinic Rotations for LLM KV Cache Compression
   → IsoQuant 用四元数把每个 4D 块表示为单位四元数并施加闭式变换 T(v)=q_L·v·q̄_R，实现 SO(4) 旋转；d=128 时前向旋转成本从 RotorQuant 的约 2408 次 FMA 降至 1024（Full）/512（Fast），在 18 种融合 CUDA 设置下平均 kernel 级加速 4.5×–4.7×（峰值超 6×）且重构 MSE 相当。


### KV Cache 压缩(非量化)（11 篇）

55. **2603.01426** Understanding the Physics of Key-Value Cache Compression for LLMs through Attention Dynamics
   → 本文提出把 KV 压缩视为对 token 级路由的受控扰动，区分保留、可及、利用三概念；合成任务实验发现：中等压缩几乎不掉精度但已退化内部表示（存在冗余）、所有模型在约 90% 压缩附近出现与全局驱逐比（GER）尖峰相关的"幻觉安全悬崖"（语义可及性的相变）、LLaMA 与 Qwen 路由动力学迥异导致抗压性不同，并识别出"表示僵化"现象。

56. **2603.10899** LookaheadKV: Fast and Accurate KV Cache Eviction by Glimpsing into the Future without Generation
   → LookaheadKV 针对 prompt KV 驱逐中"重要性估计无法预见未来需求"的问题，借鉴近期"窥视未来"思路（用草稿生成器产生替代未来响应来估计重要性），但**免去真实生成**的开销，实现快速且准确的 KV 驱逐。

57. **2603.11504** LongFlow: Efficient KV Cache Compression for Reasoning Models
   → LongFlow 针对 OpenAI-o1/DeepSeek-R1 类推理模型"长输出"场景（现有方法多为长输入短输出设计而失效），提出用当前 query 的注意力计算中间结果做高效重要性估计（开销可忽略、无需辅助存储），并把 FlashAttention、重要性估计与 token 驱逐融合为单一 kernel，在 80% KV 压缩下实现最高 11.8× 吞吐提升且精度损失很小。

58. **2603.11564** Where Matters More Than What: Decoding-aligned KV Cache Compression via Position-aware Pseudo Queries
   → 本文指出现有 KV 压缩用 prefill 阶段输入侧注意力估计重要性、无法保留未来生成所需的关键 token；发现构造逼近真实解码 query 的伪 query 时**位置信息比语义内容更关键**，据此提出解码对齐的 KV 压缩方法，用位置感知伪 query 更准确地保留生成过程真正会关注的 token。

59. **2603.14303** SemantiCache: Efficient KV Cache Compression via Semantic Chunking and Clustered Merging
   → SemantiCache 指出现有 KV 压缩作用于离散 token 或非语义块会造成"语义碎片化"（连贯语言单元被打断、信息不可逆丢失），提出按分隔符切分语义连贯块 + 块内贪心种子聚类合并的框架，使压缩过程与语言的语义层级结构对齐。

60. **2603.19664** The Residual Stream Is All You Need: On the Redundancy of the KV Cache in Transformer Inference
   → 本文证明 KV cache 这一"必需状态"完全冗余——每层的 key/value 都是残差流的确定性投影，用每 token 单个残差向量重算可**逐比特一致**（零重构误差）；在 4 个架构家族 6 个模型（135M–4B）上验证，跨任务残差修补在每层产生 D_KL=0，确立残差流为充分状态。

61. **2603.20616** Beyond Token Eviction: Mixed-Dimension Budget Allocation for Efficient KV Cache Compression
   → MixedDimKV 把 token 驱逐视为"每 token 要么零维要么满维"的粗糙降维，提出在更细粒度上为不同 token 分配不同维度数；加强版 MixedDimKV-H 进一步整合头级重要性；在 LongBench 上仅用 6.25% KV cache 即与全注意力相当，大海捞针测试中 50K 上下文仅用 0.26% 缓存仍保持 100% 准确率。

62. **2603.22910** EchoKV: Efficient KV Cache Compression via Similarity-Based Reconstruction
   → EchoKV 不同于改动模型投影的低秩压缩（无法切回全缓存），用轻量网络从保留的子集**重建被丢弃的 KV 成分**（利用注意力头层间/层内相似性），支持全缓存与压缩缓存按需切换；两阶段轻量微调在单张 A100 上对 7B 模型仅需几分钟。

63. **2603.26556** When Perplexity Lies: Generation-Focused Distillation of Hybrid Sequence Models
   → 本文揭示"困惑度会说谎"——一个 7B 蒸馏模型在对数似然评分下与教师仅差 0.2pp，自回归生成时却落后 20.8pp；作者设计 GenDistill 多阶段管线把预训练 Transformer 蒸馏为高效 Hybrid-KDA 学生，在 Qwen3-0.6B 受控平台上系统消融六个设计轴，发现对数似然评测会系统性低估师生差距甚至反转设计结论；最优配方保留教师 86–90% 知识基准精度，KV cache 显存最高降 75%、128K 上下文首 token 延迟改善 2–4×。

64. **2604.08558** WAND: Windowed Attention and Knowledge Distillation for Efficient Autoregressive Text-to-Speech Models
   → WAND 把 AR-TTS 的注意力拆分为"条件 token 的持久全局注意力 + 生成 token 的局部滑窗注意力"，配合渐进收紧窗口的课程学习与全注意力教师的知识蒸馏，使模型以恒定计算/显存复杂度运行；在三个现代 AR-TTS 模型上保持原质量的同时，KV cache 显存最高减少 66.2%、每步延迟长度不变且近恒定。

65. **2604.19769** TTKV: Temporal-Tiered KV Cache for Long-Context LLM Inference
   → TTKV 借鉴人类记忆（清晰度、回忆频率、相关性随时间邻近性变化），把 KV cache 划分为**容量与精度异构的时序层**——打破现有方法"KV 状态跨时间同等重要、统一精度与可及性"的隐含假设，实现长上下文 LLM 推理的显存优化。


### 剪枝与稀疏（14 篇）

66. **2603.01376** 3BASiL: An Algorithmic Framework for Sparse plus Low-Rank Compression of LLMs
   → 3BASiL-TM 用带收敛保证的 3 块 ADMM 最小化逐层重建误差，再用 Transformer 匹配（TM）精炼步骤跨层联合优化稀疏与低秩成分；在（2:4 稀疏 + 64 低秩）配置下，把 LLaMA-8B 相对稠密的 WikiText2 PPL 差距较此前方法缩小 30% 以上，且压缩运行时在 A100 上比 SOTA S+LR 方法快 2.5×。

67. **2603.05105** Diff-ES: Stage-wise Structural Diffusion Pruning via Evolutionary Search
   → Diff-ES 指出扩散模型各去噪步的重要性高度非均匀且依模型而异，现有方法（如 MosaicDiff）靠手工调的阶段稀疏调度、推理时拼接多个独立剪枝模型而增显存；Diff-ES 用进化搜索自动寻找分阶段结构化剪枝的稀疏调度，在真实加速与图像质量间取得更好平衡。

68. **2603.05878** ROSE: Reordered SparseGPT for More Accurate One-Shot Large Language Models Pruning
   → ROSE 发现 SparseGPT 固定的从左到右剪枝顺序在权重呈列状模式时是次优的，于是先做预剪枝识别候选权重并估计列/块剪枝损失，再执行两级重排序（块内按列损失降序、块间按块损失排序），并用块损失相对范围自适应识别列状层；在 LLaMA2-7B/13B/70B、LLaMA3-8B、Mistral-7B 上超越 SparseGPT 及其他同类剪枝方法。

69. **2603.06003** EvoESAP: Non-Uniform Expert Pruning for Sparse MoE
   → EvoESAP 把专家剪枝解耦为"层内专家排序"与"跨层预算分配"两问，指出现有方法默认均匀层间稀疏度而预算分配强烈影响性能；提出投机解码启发的 ESAP（Expected Speculative Acceptance Proxy）做非均匀层间分配，显著优于均匀基线。

70. **2603.08065** Deterministic Differentiable Structured Pruning for Large Language Models
   → DDP 把结构化剪枝视为 L0 稀疏约束下的乘性门控学习，但不用随机 hard-concrete 松弛，而是直接优化离散 L0 目标的确定性软代理，消除训练-测试失配并扩大掩码表达范围；在 Qwen3-32B 与 Qwen3-30B-A3B 等稠密/MoE 模型上 20% 稀疏度时下游任务性能损失仅约 1%，并在 vLLM 真实部署中实现端到端加速。

71. **2603.13418** GPrune-LLM: Generalization-Aware Structured Pruning for Large Language Models
   → GPrune-LLM 发现神经元存在分布敏感性差异——分布鲁棒神经元跨数据集排名稳定、分布敏感神经元排名方差大；据此把神经元划分为行为一致模块以局部化排名竞争、对激活评分不可靠的模块切换到激活无关度量、并自适应学习模块级稀疏度，在高稀疏度下持续改善压缩后泛化能力并降低对重要性度量选择的依赖。

72. **2603.18492** AIMER: Calibration-Free Task-Agnostic MoE Expert Pruning
   → AIMER 指出现有任务无关专家剪枝依赖校准集（用路由/激活统计估计重要性），决策对校准数据敏感且预处理成本高；提出基于"绝对均值与均方根之比"的免校准重要性准则，直接用权重统计即可排序专家。

73. **2603.20280** Mix-and-Match Pruning: Globally Guided Layer-Wise Sparsification of DNNs
   → Mix-and-Match Pruning 用敏感度分数与简单架构规则生成多样的高质量剪枝配置——推导架构感知的稀疏度范围（如保留归一化层、更狠剪分类层），并系统采样这些范围为每个模型产出十种策略组合，解决"不同层/架构对剪枝响应不同、单一策略次优"的问题。

74. **2603.20991** Structural Sensitivity in Compressed Transformers: Relative Error Propagation and Layer Removal
   → 本文定义 ρ = 层输出误差/输入误差，直接测量 6 个 Transformer（117M–8B）的误差传播，发现：层 t 的误差按后续各层 ρ 值的乘积向下游缩放（可预测表示漂移，Spearman r=-0.44, p<1e-4），这解释了"压缩早层伤害更大"，为层级压缩预算分配提供机理依据。

75. **2603.23985** Diet Your LLM: Dimension-wise Global Pruning of LLMs via Merging Task-specific Importance Score
   → DIET 只用每任务 100 个样本分析各任务的激活幅度，再以多数投票融合任务特异重要性分数构建单一全局掩码，实现维度级粒度 + 任务感知选择的免训练剪枝；在 Gemma-2 2B/9B 七个零样本基准上，20% 稀疏度时较此前 SOTA 结构化剪枝平均精度提升近 10%。

76. **2603.24652** Demystifying When Pruning Works via Representation Hierarchies
   → 本文把语言模型内部计算分解为嵌入（表示）、logit（softmax 前）、概率（softmax 后）三个顺序空间，发现嵌入与 logit 空间的表示对剪枝基本鲁棒、而概率空间脆弱——这解释了剪枝模型在非生成任务表现好、生成任务常失败的分歧。

77. **2603.25325** How Pruning Reshapes Features: Sparse Autoencoder Analysis of Weight-Pruned Language Models
   → 本文首次用稀疏自编码器（SAE）系统研究非结构化剪枝对 LM 内部表示的影响——跨 3 个模型家族（Gemma 3 1B/Gemma 2 2B/Llama 3.2 1B）、2 种剪枝方法（magnitude/Wanda）、6 个稀疏度（0–60%）、5 个研究问题，最惊人发现是低激活率的稀有 SAE 特征对剪枝特别脆弱。

78. **2604.03258** SoLA: Leveraging Soft Activation Sparsity and Low-Rank Decomposition for Large Language Model Compression
   → SoLA 识别并保留对推理贡献显著的少数成分、用低秩分解压缩其余多数成分，实现免训练、无需特殊硬件、无需昂贵后训练的 LLM 压缩，兼顾效率与模型质量。

79. **2604.09595** Why Smaller Is Slower? Dimensional Misalignment in Compressed LLMs
   → 本文揭示后训练压缩产生的不规则张量维度会让 GPU 执行栈效率下降（"维度失配"）——ASVD 压缩 Llama-3-8B 参数少 15% 却丝毫不快，因其 95% 维度失配；提出 GAC（GPU-Aligned Compression），用多选背包优化在相同参数预算下重选硬件对齐维度，可包装任意降维压缩器。


### Token 剪枝（8 篇）

80. **2603.01236** AgilePruner: An Empirical Study of Attention and Diversity for Adaptive Visual Token Pruning in Large Vision-Language Models
   → AgilePruner 用有效秩（erank）与注意力分数熵系统对比注意力式与多样性式视觉 token 剪枝，发现：许多多样性方法实际保留的特征多样性远低于预期、且其保留的多样性与幻觉频率上升相关；注意力式适合视觉证据集中的简单图、多样性式适合特征分布的复杂图；据此提出图像感知的自适应剪枝，在标准与幻觉评测上均稳健领先。

81. **2603.03681** EvoPrune: Early-Stage Visual Token Pruning for Efficient MLLMs
   → EvoPrune 指出多数视觉 token 剪枝在编码之后才进行，忽视了编码阶段本身的巨大计算成本；EvoPrune 直接在视觉编码过程中做逐层剪枝（由 token 相似度、多样性与注意力重要性引导），把压缩窗口前移以节省编码开销。

82. **2603.05950** Energy-Driven Adaptive Visual Token Pruning for Efficient Vision-Language Models
   → E-AdaPrune 指出多数视觉 token 削减方法对所有输入用固定预算、忽视图像信息密度差异，提出从视觉特征空间的**奇异值谱**决定 token 预算——保留固定比例谱能量，信息密集场景多分 token、冗余场景激进压缩，零额外可学习参数；在 9 个基准、3 个 VLM 骨干（含 LLaVA-1.5-7B）上验证有效。

83. **2603.21105** ResPrune: Text-Conditioned Subspace Reconstruction for Visual Token Pruning in Large Vision-Language Models
   → ResPrune 把视觉 token 剪枝建模为**子空间重构问题**——用残差能量引导的贪心子空间扩展选择 token 子集，保持原视觉 token 空间的几何结构；进一步融入文本条件的跨模态对齐，实现免训练的高效 LVLM 推理。

84. **2603.22911** ForestPrune: High-ratio Visual Token Compression for Video Multimodal Large Language Models via Spatial-Temporal Forest Modeling
   → ForestPrune 把视频 token 压缩的短板归因于对时序与连续视频内容建模不足，提出免训练的时空森林建模——跨帧构建 token 森林（语义/空间/时序约束），再按树深度与节点角色评估重要性、得到全局最优剪枝决策；在 LLaVA-OneVision 上减少 90% token 仍保留 95.8% 平均精度，在 LLaVA-Video 上较 FrameFusion 精度 +10.1%、剪枝耗时 -81.4%。

85. **2603.24680** ReDiPrune: Relevance-Diversity Pre-Projection Token Pruning for Efficient Multimodal LLMs
   → ReDiPrune 在视觉-语言投影**之前**（视觉特征仍丰富可辨时）做免训练 token 剪枝，用轻量规则联合**文本条件相关性**与**最大-最小多样性**打分，确保所选 token 既贴合查询又互不冗余，保留细粒度空间与语义线索。

86. **2603.27650** V-CAST: Video Curvature-Aware Spatio-Temporal Pruning for Efficient Video Large Language Models
   → V-CAST 指出紧预算下视频 token 压缩的瓶颈是**时空信息覆盖不足**——粗粒度逐帧分配或场景切分造成覆盖不连续，token 合并还会在 MRoPE 式离散 (t,h,w) 绑定下错位时空坐标；V-CAST 以曲率感知做免训练、即插即用的时空剪枝，保持连续覆盖。

87. **2603.27900** Rényi Entropy: A New Token Pruning Metric for Vision Transformers
   → 本文指出依赖 [CLS] token 估计 patch 重要性在浅层不可靠（语义表示尚不成熟），提出源自 Rényi 熵的免训练度量 Col-Ln，能从网络第一层就识别信息性 token、实现更可靠的早期剪枝；在 ViT 与大型视觉语言模型上持续超越 SOTA 剪枝方法。


### 知识蒸馏（11 篇）

88. **2603.01875** KDFlow: A User-Friendly and Efficient Knowledge Distillation Framework for Large Language Models
   → KDFlow 指出学生/教师在 KD 中角色不同却共用同一训练后端（FSDP/DeepSpeed）导致效率次优，于是用解耦架构——SGLang 跑教师推理、FSDP2 跑学生训练，且只零拷贝传输教师隐状态、在学生侧重算 logits——实现 1.44×–6.36× 于现有 KD 框架的加速，并支持 off/on-policy 与跨 tokenizer 蒸馏。

89. **2603.05421** DARK: Diagonal-Anchored Repulsive Knowledge Distillation for Vision-Language Models under Extreme Compression
   → DARK 主张在师生容量差达一个数量级时"严格模仿教师是坏目标"，把蒸馏损失分解为对角项（匹配的图文对，全程锚定对齐）与非对角项（非目标相似性，权重从正退火到负、从模仿转为排斥教师的非目标结构）；用它把 427M 胎儿超声 VLM FetalCLIP 蒸馏为 75M 的 MobileFetalCLIP（视觉编码器小 26×、iPhone 16 Pro 上 1.6 ms），在三个零样本基准上反超教师（如 HC18 88.6% vs 83.5%）。

90. **2603.08083** High-Fidelity Pruning for Large Language Models
   → 本文指出用 Taylor 展开 + one-hot 交叉熵估计神经元重要性只关注单个预测 token 的概率、忽视模型其他潜在预测；直觉的替代是自蒸馏准则，但引入显著成本——本文提出高保真剪枝方法，在保留自蒸馏式全分布评估优点的同时控制其开销。

91. **2603.08258** WaDi: Weight Direction-aware Distillation for One-step Image Synthesis
   → WaDi 分析一步学生与多步教师之间 U-Net/DiT 的权重变化，发现**权重方向变化显著大于范数变化**——方向是蒸馏中的关键因素；据此提出低秩方向旋转适配器 LoRaD，以参数高效的方式适配一步扩散学生。

92. **2603.11881** Bielik-Minitron-7B: Compressing Large Language Models via Structured Pruning and Knowledge Distillation for the Polish Language
   → Bielik-Minitron-7B 借鉴 NVIDIA Minitron 两阶段方法，用结构化混合剪枝 + logit 蒸馏把 Bielik-11B-v3.0 从 11.04B 压缩到 7.35B（-33.4% 参数），再经 SFT、DPO-P、GRPO 对齐管线，恢复基线约 90% 的性能并实现最高 50% 推理加速，为小语种语言模型提供了低成本压缩路径。

93. **2603.21426** Uncertainty-Aware Knowledge Distillation for Multimodal Large Language Models
   → Beta-KD 从贝叶斯视角统一师生学习，把教师监督解释为 Gibbs 先验，按样本的教师不确定性与数据噪声自适应调节学生对教师指导的依赖程度，解决"数据监督与教师监督最优平衡难定"的问题。

94. **2603.22056** Dual-Space Knowledge Distillation with Key-Query Matching for Large Language Models with Vocabulary Mismatch
   → 本文系统分析词表不匹配蒸馏 SOTA 方法 DSKD-CMA 的注意力机制——通过手工 token 对齐探针与热力图可视化揭示其优势与局限，并提出 Key-Query 匹配的改进，推进跨 tokenizer 知识蒸馏的可理解性与效果。

95. **2603.22355** Demystifying Low-Rank Knowledge Distillation in Large Language Models: Convergence, Generalization, and Information-Theoretic Guarantees
   → 本文为低秩知识蒸馏（如 Low-Rank Clone）建立严格理论框架——证明温和假设下低秩投影保留优化动态（收敛率 O(1/√T)）、泛化误差随秩 r 按 O(r(m+n)/√n) 缩放、信息论上激活克隆最大化师生中间表示互信息，并给出最优秩 r* = O(√n) 的指导；标准语言建模基准实验与理论预测高度吻合。

96. **2603.25562** Revisiting On-Policy Distillation: Empirical Failure Modes and Simple Fixes
   → 本文从理论与实现双面重审 OPD——标准实现把分布匹配简化为采样 token 对数比，在长 rollout（前缀漂移出教师支撑集）上信号脆弱；理论上 token 级 OPD 相对序列级 reverse-KL 有偏但方差界更紧，受控合成研究显示更强的未来奖励相关性可缓解；据此给出简单修复。

97. **2603.26778** TED: Training-Free Experience Distillation for Multimodal Reasoning
   → TED 把蒸馏的更新目标从模型参数转移到注入学生提示词的"上下文经验"——学生对每个输入生成多条推理轨迹，教师独立解题后把经验提炼进上下文，无需任何参数更新与大规模训练数据，实现资源受限环境下的多模态推理蒸馏。

98. **2604.00223** Diversity-Aware Reverse Kullback-Leibler Divergence for Large Language Model Distillation
   → 本文把反向 KL（RKL）的梯度分解为目标与非目标分量，发现**非目标梯度在学生已匹配教师时仍持续推高目标 logit**——这是 RKL 导致学生过度自信的结构性根源；据此提出多样性感知的 RKL 改进，在保持 RKL 优势的同时恢复预测多样性。


### 早退机制（3 篇）

99. **2603.21365** TIDE: Token-Informed Depth Execution for Per-Token Early Exit in LLM Inference
   → TIDE 在周期性检查点层挂接微型学习路由器，推理时为每个 token 选择隐藏状态已收敛的最早退出层；免重训练、兼容任意 HuggingFace 因果 LM、自动检测 GPU、支持 fp32/fp16/bf16 融合 CUDA kernel；在 A100 + DeepSeek R1 Distill 8B 上 prefill 100% 退出（5% 在第 11 层、其余在第 31 层），prefill 延迟降 7.2%、单批吞吐升 6.6%。

100. **2603.23701** The Diminishing Returns of Early-Exit Decoding in Modern LLMs
   → 本文重新评估逐层 early-exit（预测足够置信即提前停算），发现随着新模型采用更优预训练配方与架构、层冗余下降，early-exit 有效性呈逐代递减趋势；作者提出量化模型内在 early-exit 适配度的指标与基准，并发现稠密 Transformer 比 MoE/SSM 更具 early-exit 潜力、>20B 大模型与未专调基座模型潜力更高。

101. **2604.18592** Two-dimensional early exit optimisation of LLM inference
   → 本文提出二维 early exit——逐句增量处理输入的同时渐进激活更深层，协调"层级退出"与"句级退出"获得超过任一单维的乘性算力节省；在 4 个 SOTA LLM（Llama 3.1/3.2、Gemma、Qwen，3B–8B）、3 个情感分类数据集上，较最优层级 early exit 再提速 1.4–2.3×（简单任务），复杂任务上优雅退化。
