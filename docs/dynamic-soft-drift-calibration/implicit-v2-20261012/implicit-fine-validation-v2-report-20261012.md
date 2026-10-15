# 动态软约束漂移解级反馈精度修订完整报告

2026年10月12日。本轮状态为`qualified_solution_feedback_v2`。执行完整性为True，完整数值资格为True。正式q学习及业务分类矩阵均未启动，没有新业务F1结果。

## 问题与版本区别

本轮保留原充分求解LR加隐式微分。第一版stop_implicit_gradient_not_verified保持不变，旧粗细风险变化指标和失败记录不改写。第二版新增细档f到实际一次Newton校验状态v的稳定性检查，不将v作为新业务模型选优。

原六类、96维十块、P/G基础映射、样本质量、t、mu/scale、内容划分及软惩罚保持不变。目标为带权CE加0.0005(1+t)乘原W平方，bias不正则。485维精确对比数值参数化和q=1训练Cholesky坐标不变。

480行训练槽位、8行源内留出反馈仍沿用旧成员，调整pre占总CE质量1/30。实际目标排除标签不是被读取的目标数据；所有重复、两侧、内部flow整体划分。

| role_id                          | target_excluded   | group   | source_calibration   |   t |
|:---------------------------------|:------------------|:--------|:---------------------|----:|
| main/f0/shadowsocks/G0/i1/trojan | shadowsocks       | G0      | trojan               |   4 |
| main/f0/shadowsocks/G2/i1/trojan | shadowsocks       | G2      | trojan               |   0 |
| main/f0/vless/G1/i1/shadowsocks  | vless             | G1      | shadowsocks          |   4 |
| main/f0/trojan/G0/i1/shadowsocks | trojan            | G0      | shadowsocks          |   4 |
| main/f0/trojan/G2/i1/shadowsocks | trojan            | G2      | shadowsocks          |   4 |
| main/f0/vmess/G1/i1/shadowsocks  | vmess             | G1      | shadowsocks          |   1 |

## CUDA环境和计算政策

Python D:\Tools\Anaconda\envs\Pytorch312\python.exe；PyTorch 2.5.1；CUDA 12.4；GPU NVIDIA GeForce RTX 4060 Ti。全部训练、推理、Hessian、系统求解和微分CUDA float64，无CPU数值回退。

旧三fine直接复用。其他q点保持原v4 max_iter=2000、max_eval=10000、原梯度1e-5验收；随后保持同目标Newton/Armijo策略，最多30次更新到原梯度1e-9。粗档1e-8仅记录实际独立观察到的状态，不复制fine制造另一层级。

## 一次独立细档校验

每个fine点重算原残差和Hessian，显式公式与AD独立核对；解H delta=−r并与CUDA通用线性求解比较。每点只执行一次完整步长1更新，没有回溯、jitter、第二次校正或源内CE选步长。

校验系统后向误差门1e-12，两解校正相对差门1e-8；f/v原梯度均不超过1e-9。平台标签还要求原梯度不超过1e-12、相对校正不超过1e-10和目标在固定舍入尺度内。平台标签本身不构成资格，风险相等也不能替代独立求解证据。

| role_id                          | arm   | key              |     gradient_f |     gradient_v |    risk_change |   Newton_backward_error |   independent_step_relative | floating_platform   | passed   |
|:---------------------------------|:------|:-----------------|---------------:|---------------:|---------------:|------------------------:|----------------------------:|:--------------------|:---------|
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt-all-h0-minus | 5.28493265e-14 | 1.05086296e-16 | 8.65973959e-15 |          2.80822361e-18 |              1.41011795e-14 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt-all-h0-plus  | 5.27996971e-14 | 9.60061024e-17 | 7.77156117e-15 |          2.12106674e-18 |              1.09545564e-14 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt-all-h1-minus | 5.28260161e-14 | 9.33498071e-17 | 6.99440506e-15 |          1.73484019e-18 |              5.38009634e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt-all-h1-plus  | 5.27821602e-14 | 1.46014928e-16 | 8.77076189e-15 |          2.17954007e-18 |              1.02522715e-14 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt-alt-h0-minus | 5.31446089e-14 | 7.71138795e-17 | 7.66053887e-15 |          2.07262212e-18 |              8.0726332e-15  | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt-alt-h0-plus  | 5.2457794e-14  | 1.41596804e-16 | 7.21644966e-15 |          1.93396708e-18 |              1.11590212e-14 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt-alt-h1-minus | 5.28844817e-14 | 1.10453096e-16 | 6.77236045e-15 |          5.01212708e-18 |              8.8677915e-15  | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt-alt-h1-plus  | 5.27525885e-14 | 1.64039789e-16 | 8.43769499e-15 |          2.46892507e-18 |              1.12095705e-14 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt-center       | 5.28534464e-14 | 1.76399693e-16 | 6.66133815e-15 |          4.51702887e-18 |              1.15421388e-14 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one-all-h0-minus | 1.94800773e-14 | 9.84726623e-17 | 2.55351296e-15 |          1.23799768e-16 |              2.5552408e-15  | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one-all-h0-plus  | 2.53924486e-14 | 7.59077046e-17 | 3.10862447e-15 |          6.48716185e-17 |              6.99257721e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one-all-h1-minus | 2.47091844e-14 | 1.1434606e-16  | 2.55351296e-15 |          6.26718073e-17 |              5.55512436e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one-all-h1-plus  | 2.49158333e-14 | 7.85504474e-17 | 3.33066907e-15 |          1.06440532e-16 |              2.5635478e-15  | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one-alt-h0-minus | 1.89819948e-14 | 7.36173275e-17 | 1.11022302e-16 |          6.38361845e-17 |              5.22290028e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one-alt-h0-plus  | 3.36098337e-14 | 6.76542156e-17 | 4.10782519e-15 |          6.41095435e-17 |              5.13133527e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one-alt-h1-minus | 2.5345611e-14  | 1.07986536e-16 | 2.22044605e-15 |          9.64715015e-17 |              7.72602448e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one-alt-h1-plus  | 1.7238164e-14  | 1.02131845e-16 | 3.99680289e-15 |          9.78940664e-17 |              3.88889552e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one-center       | 2.48104488e-14 | 7.98379375e-17 | 2.99760217e-15 |          6.30470479e-17 |              3.41325777e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt-all-h0-minus | 3.84072521e-14 | 2.1209705e-16  | 4.77395901e-15 |          1.7967469e-18  |              6.52308165e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt-all-h0-plus  | 3.84793244e-14 | 1.83880688e-16 | 5.21804822e-15 |          1.80290901e-18 |              9.5552962e-15  | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt-all-h1-minus | 3.84222276e-14 | 1.18245799e-16 | 3.99680289e-15 |          2.49827136e-18 |              1.61072593e-14 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt-all-h1-plus  | 3.84467171e-14 | 7.58941521e-17 | 5.55111512e-15 |          2.0264069e-18  |              8.29810447e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt-alt-h0-minus | 3.84312401e-14 | 1.0495077e-16  | 5.21804822e-15 |          2.48783679e-18 |              9.17912702e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt-alt-h0-plus  | 3.83937944e-14 | 1.42030485e-16 | 5.55111512e-15 |          3.00952831e-18 |              9.27638283e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt-alt-h1-minus | 3.84422989e-14 | 1.05357346e-16 | 5.88418203e-15 |          2.05473774e-18 |              1.0031529e-14  | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt-alt-h1-plus  | 3.83765421e-14 | 9.61687327e-17 | 5.10702591e-15 |          2.44934457e-18 |              6.34745651e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt-center       | 3.84171861e-14 | 1.51788304e-16 | 4.5519144e-15  |          2.1160447e-18  |              1.00355668e-14 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one-all-h0-minus | 5.45830742e-15 | 9.86081876e-17 | 2.22044605e-15 |          4.90456966e-17 |              6.66898266e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one-all-h0-plus  | 5.73651369e-15 | 1.32929963e-16 | 5.55111512e-16 |          9.57725797e-17 |              3.59255759e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one-all-h1-minus | 5.81717834e-15 | 1.35200011e-16 | 1.11022302e-15 |          5.43587655e-17 |              2.66957137e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one-all-h1-plus  | 5.85859486e-15 | 7.39019306e-17 | 1.77635684e-15 |          8.30826627e-17 |              3.67588938e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one-alt-h0-minus | 2.72937055e-15 | 1.06062078e-16 | 1.88737914e-15 |          5.03678524e-17 |              4.03033757e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one-alt-h0-plus  | 3.86355444e-14 | 9.82829269e-17 | 8.54871729e-15 |          6.65280127e-17 |              4.03728909e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one-alt-h1-minus | 5.61529989e-15 | 1.13448205e-16 | 2.77555756e-15 |          7.91898625e-17 |              2.56423373e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one-alt-h1-plus  | 5.18617267e-15 | 1.08637058e-16 | 3.88578059e-15 |          1.06325879e-16 |              7.05954894e-15 | True                | True     |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one-center       | 5.86314851e-15 | 1.51300413e-16 | 4.4408921e-16  |          7.13918666e-17 |              5.46986036e-15 | True                | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt-all-h0-minus | 6.23059227e-12 | 8.21825247e-17 | 3.7897796e-11  |          9.93538412e-18 |              1.93971034e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt-all-h0-plus  | 6.26522911e-12 | 8.37004077e-17 | 3.72213371e-11 |          7.08989312e-18 |              1.64627885e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt-all-h1-minus | 6.24982436e-12 | 6.13793955e-17 | 3.77290421e-11 |          1.70907345e-17 |              3.25931561e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt-all-h1-plus  | 6.26576895e-12 | 7.62736228e-17 | 3.75342535e-11 |          1.14443528e-17 |              1.86936686e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt-alt-h0-minus | 6.23415595e-12 | 9.87166078e-17 | 3.77272658e-11 |          8.80589863e-18 |              2.70883214e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt-alt-h0-plus  | 6.27684805e-12 | 5.57279917e-17 | 3.74925646e-11 |          8.04579133e-18 |              1.84211454e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt-alt-h1-minus | 6.2513421e-12  | 1.50452321e-16 | 3.76685905e-11 |          1.5862988e-17  |              2.86112672e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt-alt-h1-plus  | 6.26525719e-12 | 7.45018417e-17 | 3.76006448e-11 |          1.00637294e-17 |              2.63908892e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt-center       | 6.25841161e-12 | 8.63024929e-17 | 3.76385034e-11 |          7.5114471e-18  |              1.64124519e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one-all-h0-minus | 8.31707985e-12 | 6.08982808e-17 | 5.55387958e-09 |          3.96649058e-17 |              1.02454201e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one-all-h0-plus  | 1.56416307e-11 | 9.5843472e-17  | 9.8530335e-09  |          4.91670861e-17 |              1.7663462e-14  | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one-all-h1-minus | 7.94614618e-12 | 9.02056208e-17 | 1.17990884e-09 |          7.81098155e-17 |              1.02854578e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one-all-h1-plus  | 1.72896485e-11 | 5.75846879e-17 | 1.10909264e-08 |          4.41307547e-17 |              1.19028811e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one-alt-h0-minus | 4.48302359e-12 | 8.89045781e-17 | 3.08917247e-09 |          4.7875765e-17  |              2.38141834e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one-alt-h0-plus  | 1.35914975e-11 | 5.85469173e-17 | 8.69057959e-09 |          4.55638314e-17 |              1.41772789e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one-alt-h1-minus | 8.25472413e-12 | 7.00394603e-17 | 5.44871814e-09 |          5.97952995e-17 |              9.90352e-15    | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one-alt-h1-plus  | 4.31034527e-12 | 7.63278329e-17 | 2.1146267e-09  |          5.04407992e-17 |              1.26772108e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one-center       | 2.05643509e-11 | 7.89299182e-17 | 1.31948594e-08 |          4.39987754e-17 |              1.48056247e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt-all-h0-minus | 3.49785493e-12 | 1.24141149e-16 | 5.50515189e-12 |          5.10685768e-18 |              1.75435599e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt-all-h0-plus  | 4.089423e-12   | 8.97719399e-17 | 1.15418786e-12 |          1.08415025e-17 |              2.02069197e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt-all-h1-minus | 4.63340133e-12 | 9.99634403e-17 | 6.19237994e-12 |          7.32517177e-18 |              1.92758459e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt-all-h1-plus  | 5.2704371e-12  | 8.01767507e-17 | 1.74954495e-12 |          1.01900268e-17 |              2.15400959e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt-alt-h0-minus | 3.62452658e-12 | 1.08311797e-16 | 7.05047132e-13 |          7.91951782e-18 |              2.9988967e-13  | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt-alt-h0-plus  | 3.37672596e-12 | 7.81303191e-17 | 7.09343695e-12 |          1.2664192e-17  |              2.21202632e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt-alt-h1-minus | 4.18818088e-12 | 9.19538968e-17 | 4.74537076e-12 |          8.01184546e-18 |              1.5319452e-13  | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt-alt-h1-plus  | 4.58298407e-12 | 9.09645623e-17 | 5.13944443e-12 |          7.95701899e-18 |              1.58995306e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt-center       | 5.49930369e-12 | 9.76053006e-17 | 2.17668106e-11 |          7.60588511e-18 |              2.10974319e-13 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one-all-h0-minus | 2.38190478e-11 | 8.02309608e-17 | 1.2065184e-08  |          8.83380758e-17 |              1.56159561e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one-all-h0-plus  | 3.40297918e-11 | 1.32055825e-16 | 8.77626216e-09 |          5.51461058e-17 |              5.93771877e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one-all-h1-minus | 2.20661008e-11 | 4.79759461e-17 | 1.11515754e-08 |          3.89274938e-17 |              2.700941e-14   | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one-all-h1-plus  | 2.75692177e-11 | 9.44340092e-17 | 1.20585455e-08 |          4.07714591e-17 |              2.35662276e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one-alt-h0-minus | 3.87488321e-11 | 1.25767452e-16 | 1.05950586e-08 |          5.09125104e-17 |              5.09912664e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one-alt-h0-plus  | 2.96682021e-11 | 6.83047369e-17 | 1.11336069e-08 |          5.130292e-17   |              2.3976241e-14  | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one-alt-h1-minus | 2.55991226e-11 | 5.48606299e-17 | 1.28377451e-08 |          6.39364816e-17 |              3.97274732e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one-alt-h1-plus  | 2.13918995e-11 | 4.78133158e-17 | 1.16087779e-08 |          4.8617682e-17  |              2.66837536e-14 | False               | True     |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one-center       | 1.99818498e-11 | 7.34004871e-17 | 1.24538826e-08 |          4.44102122e-17 |              1.92624103e-14 | False               | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt-all-h0-minus | 3.30256655e-14 | 1.19262239e-16 | 4.02788913e-13 |          2.3946823e-17  |              4.03930172e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt-all-h0-plus  | 3.31091491e-14 | 1.96349013e-16 | 4.00457445e-13 |          2.33859899e-17 |              5.03914016e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt-all-h1-minus | 3.31709486e-14 | 1.33573708e-16 | 4.03677092e-13 |          2.58692484e-17 |              4.56292797e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt-all-h1-plus  | 3.31956684e-14 | 1.5460723e-16  | 4.00457445e-13 |          2.46464357e-17 |              5.64058261e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt-alt-h0-minus | 3.29862006e-14 | 1.34522385e-16 | 3.99569267e-13 |          2.30066881e-17 |              3.77557496e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt-alt-h0-plus  | 3.29410978e-14 | 1.2968752e-16  | 4.04343226e-13 |          2.31717299e-17 |              4.62796241e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt-alt-h1-minus | 3.32236409e-14 | 2.34702665e-16 | 4.00790512e-13 |          2.24980972e-17 |              4.13966039e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt-alt-h1-plus  | 3.31605403e-14 | 2.08044844e-16 | 4.03677092e-13 |          2.41300726e-17 |              5.56578376e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt-center       | 3.32262429e-14 | 9.69886606e-17 | 4.03455047e-13 |          2.74995557e-17 |              4.57155034e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one-all-h0-minus | 7.7149875e-14  | 2.08586945e-16 | 1.26010313e-13 |          6.99008969e-17 |              4.98673725e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one-all-h0-plus  | 1.43173017e-13 | 1.50948047e-16 | 3.61266572e-13 |          5.72289508e-17 |              5.40063514e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one-all-h1-minus | 1.48848598e-13 | 1.91036423e-16 | 3.50275364e-13 |          6.89600804e-17 |              3.55272158e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one-all-h1-plus  | 1.65722254e-13 | 1.54390389e-16 | 3.41726647e-13 |          6.09087359e-17 |              2.45001462e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one-alt-h0-minus | 1.46135274e-13 | 1.75559437e-16 | 3.68594044e-13 |          7.37251081e-17 |              2.63921207e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one-alt-h0-plus  | 7.92746944e-14 | 5.59448321e-17 | 1.33448808e-13 |          7.25044994e-17 |              3.34101965e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one-alt-h1-minus | 1.64896525e-13 | 8.03935911e-17 | 3.40949491e-13 |          8.45768923e-17 |              5.91033653e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one-alt-h1-plus  | 1.46553342e-13 | 1.61762964e-16 | 3.43947093e-13 |          7.70995038e-17 |              5.91867102e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one-center       | 1.82676357e-13 | 1.59459035e-16 | 3.71036535e-13 |          8.40915362e-17 |              3.14249704e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt-all-h0-minus | 5.55400994e-13 | 6.75186903e-17 | 5.07149878e-13 |          1.53074082e-17 |              3.69248478e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt-all-h0-plus  | 5.28163667e-13 | 1.77782051e-16 | 4.43645121e-13 |          1.29014238e-17 |              3.35136251e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt-all-h1-minus | 5.22668063e-13 | 1.43629683e-16 | 4.41868764e-13 |          1.36071482e-17 |              3.21197249e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt-all-h1-plus  | 5.17185036e-13 | 8.86877377e-17 | 4.27879954e-13 |          1.3253447e-17  |              2.33944522e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt-alt-h0-minus | 5.59120675e-13 | 1.84314369e-16 | 4.94271291e-13 |          1.45206371e-17 |              2.83345047e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt-alt-h0-plus  | 2.11227086e-13 | 2.22884862e-16 | 1.48769885e-13 |          1.87567692e-17 |              3.23285046e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt-alt-h1-minus | 5.1971101e-13  | 1.70436582e-16 | 4.29656311e-13 |          1.34381187e-17 |              2.42240112e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt-alt-h1-plus  | 5.32087178e-13 | 9.4325589e-17  | 4.58966198e-13 |          1.43605952e-17 |              3.20258445e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt-center       | 5.17761832e-13 | 6.98226199e-17 | 4.31876757e-13 |          1.46493234e-17 |              2.85289597e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one-all-h0-minus | 1.07862287e-13 | 8.21825247e-17 | 2.05269135e-12 |          9.04042104e-17 |              5.51907907e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one-all-h0-plus  | 1.05372525e-13 | 1.13515967e-16 | 1.95998773e-12 |          7.23366523e-17 |              7.20027447e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one-all-h1-minus | 1.06994275e-13 | 1.80031771e-16 | 2.0176083e-12  |          7.90487206e-17 |              6.31326078e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one-all-h1-plus  | 1.06273714e-13 | 2.82976767e-16 | 1.99373851e-12 |          9.06199704e-17 |              1.10244797e-14 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one-alt-h0-minus | 1.04787706e-13 | 8.32667268e-17 | 1.95632399e-12 |          9.80133558e-17 |              9.24883505e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one-alt-h0-plus  | 1.08336517e-13 | 1.89952221e-16 | 2.05424566e-12 |          7.93039972e-17 |              3.97245139e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one-alt-h1-minus | 1.06096121e-13 | 1.02619736e-16 | 1.99196215e-12 |          8.19325144e-17 |              4.18792723e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one-alt-h1-plus  | 1.07183359e-13 | 1.43331527e-16 | 2.02593498e-12 |          8.11205818e-17 |              6.63197448e-15 | True                | True     |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one-center       | 1.06641258e-13 | 2.63298498e-16 | 2.00672812e-12 |          7.28423351e-17 |              3.82711263e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt-all-h0-minus | 6.64687489e-14 | 1.65015571e-16 | 1.02140518e-14 |          2.45450789e-17 |              4.82338365e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt-all-h0-plus  | 6.65074549e-14 | 1.14058069e-16 | 1.57651669e-14 |          2.41618829e-17 |              3.96509981e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt-all-h1-minus | 6.64641953e-14 | 9.45424294e-17 | 1.24344979e-14 |          2.10468389e-17 |              2.84975295e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt-all-h1-plus  | 6.65018171e-14 | 2.37873957e-16 | 1.15463195e-14 |          2.42864789e-17 |              4.5813653e-15  | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt-alt-h0-minus | 6.65039855e-14 | 7.13405029e-17 | 1.55431223e-14 |          2.52574011e-17 |              2.43968101e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt-alt-h0-plus  | 6.64998655e-14 | 7.22078647e-17 | 1.13242749e-14 |          2.97779874e-17 |              3.62276321e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt-alt-h1-minus | 6.64969382e-14 | 8.9338259e-17  | 1.39888101e-14 |          2.50267048e-17 |              2.77008303e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt-alt-h1-plus  | 6.64691826e-14 | 1.32381085e-16 | 1.02140518e-14 |          2.03626843e-17 |              3.16269371e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt-center       | 6.64982392e-14 | 8.48930301e-17 | 1.22124533e-14 |          2.35841279e-17 |              3.19311706e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one-all-h0-minus | 3.18186233e-14 | 9.96381797e-17 | 4.77395901e-14 |          8.21885111e-17 |              3.46718036e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one-all-h0-plus  | 3.23034785e-14 | 1.87133295e-16 | 4.50750548e-14 |          5.5564268e-17  |              2.59148033e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one-all-h1-minus | 3.20435952e-14 | 1.17527515e-16 | 5.17363929e-14 |          5.77194032e-17 |              2.14199327e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one-all-h1-plus  | 3.21529912e-14 | 1.39211559e-16 | 4.57411886e-14 |          6.80152625e-17 |              2.82549025e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one-alt-h0-minus | 3.16428741e-14 | 7.91467586e-17 | 5.12923037e-14 |          6.55711428e-17 |              2.64061478e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one-alt-h0-plus  | 3.24129829e-14 | 7.91467586e-17 | 4.97379915e-14 |          8.41263093e-17 |              7.31416641e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one-alt-h1-minus | 3.19451497e-14 | 1.24032729e-16 | 4.48530102e-14 |          6.25377654e-17 |              2.18664149e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one-alt-h1-plus  | 3.22037319e-14 | 1.59052459e-16 | 5.06261699e-14 |          5.58215159e-17 |              2.93464023e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one-center       | 3.20960706e-14 | 4.42354486e-17 | 4.75175455e-14 |          5.08789091e-17 |              4.60035369e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt-all-h0-minus | 1.92223624e-14 | 1.13732808e-16 | 1.17017507e-13 |          1.82946221e-17 |              2.08005476e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt-all-h0-plus  | 1.92308192e-14 | 5.990217e-17   | 1.17017507e-13 |          2.25343101e-17 |              2.43389583e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt-all-h1-minus | 1.92250729e-14 | 7.63955956e-17 | 1.15685239e-13 |          1.97126081e-17 |              2.17243408e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt-all-h1-plus  | 1.92077257e-14 | 1.78242837e-16 | 1.19459997e-13 |          1.9340148e-17  |              3.0156266e-15  | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt-alt-h0-minus | 1.92244224e-14 | 8.89045781e-17 | 1.17239551e-13 |          1.75794787e-17 |              2.76793664e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt-alt-h0-plus  | 1.91843069e-14 | 1.72604986e-16 | 1.19237953e-13 |          1.9844673e-17  |              2.96532008e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt-alt-h1-minus | 1.91879932e-14 | 1.63931368e-16 | 1.2057022e-13  |          1.98725498e-17 |              2.57689095e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt-alt-h1-plus  | 1.91904869e-14 | 1.93855348e-16 | 1.20348176e-13 |          2.02439028e-17 |              2.79867571e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt-center       | 1.92019794e-14 | 1.17527515e-16 | 1.16351373e-13 |          1.88081396e-17 |              1.99067791e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one-all-h0-minus | 2.84384061e-14 | 6.3859508e-17  | 6.55031585e-14 |          9.39134636e-17 |              3.04354623e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one-all-h0-plus  | 2.80444071e-14 | 7.32920669e-17 | 7.34967642e-14 |          1.20674081e-16 |              3.13683212e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one-all-h1-minus | 2.8346249e-14  | 1.42247325e-16 | 7.21644966e-14 |          1.07843542e-16 |              3.18010892e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one-all-h1-plus  | 2.80715121e-14 | 2.11636264e-16 | 6.92779167e-14 |          1.18903331e-16 |              3.45245941e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one-alt-h0-minus | 2.82135426e-14 | 9.19403442e-17 | 7.34967642e-14 |          1.21995593e-16 |              3.00895768e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one-alt-h0-plus  | 2.83447311e-14 | 9.97465999e-17 | 6.66133815e-14 |          1.17693688e-16 |              2.48552913e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one-alt-h1-minus | 2.8134179e-14  | 2.6454533e-16  | 6.83897383e-14 |          1.02718906e-16 |              3.76573582e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one-alt-h1-plus  | 2.83833287e-14 | 2.47198095e-16 | 6.86117829e-14 |          1.04883421e-16 |              4.25537503e-15 | True                | True     |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one-center       | 2.8185787e-14  | 6.4401609e-17  | 6.97220059e-14 |          1.02872926e-16 |              2.48519688e-15 | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt-all-h0-minus | 1.07811018e-13 | 1.20238021e-16 | 9.20263865e-13 |          2.74594085e-17 |              3.1200274e-15  | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt-all-h0-plus  | 5.55889319e-13 | 1.92066415e-16 | 4.30877556e-12 |          2.57543187e-17 |              5.03860715e-15 | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt-all-h1-minus | 2.52996964e-13 | 1.03622623e-16 | 2.03392858e-12 |          2.81257255e-17 |              4.0897832e-15  | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt-all-h1-plus  | 1.17618046e-12 | 1.80763607e-16 | 8.80795437e-12 |          2.84561004e-17 |              4.86619636e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt-alt-h0-minus | 3.76190805e-13 | 1.48698328e-16 | 2.94142488e-12 |          2.92859434e-17 |              3.7829587e-15  | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt-alt-h0-plus  | 1.99569013e-13 | 1.30172023e-16 | 1.62669878e-12 |          3.02626476e-17 |              2.96144257e-15 | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt-alt-h1-minus | 1.32552363e-12 | 1.11889664e-16 | 9.8490105e-12  |          2.7242787e-17  |              7.91883574e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt-alt-h1-plus  | 2.80517281e-13 | 2.91270914e-16 | 2.23154828e-12 |          3.08329559e-17 |              3.02806465e-15 | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt-center       | 1.79429713e-13 | 1.02348685e-16 | 1.46749279e-12 |          3.13426637e-17 |              2.41622449e-15 | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one-all-h0-minus | 5.08056775e-12 | 9.04224612e-17 | 4.13580281e-12 |          1.3118087e-16  |              3.67731041e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one-all-h0-plus  | 4.80704036e-12 | 2.03579287e-16 | 3.84214882e-12 |          1.18826639e-16 |              4.17051951e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one-all-h1-minus | 4.97659268e-12 | 7.84962373e-17 | 4.02500255e-12 |          1.58996664e-16 |              5.49878461e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one-all-h1-plus  | 4.89407772e-12 | 1.06251813e-16 | 3.93440835e-12 |          1.40259169e-16 |              3.78369452e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one-alt-h0-minus | 4.85047897e-12 | 2.79832581e-16 | 3.88133969e-12 |          1.53369926e-16 |              3.43728315e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one-alt-h0-plus  | 5.03493521e-12 | 1.85994883e-16 | 4.09461354e-12 |          1.43401792e-16 |              4.59239291e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one-alt-h1-minus | 4.90746618e-12 | 2.45897053e-16 | 3.94895228e-12 |          1.5851151e-16  |              4.08727822e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one-alt-h1-plus  | 4.96298354e-12 | 1.79977561e-16 | 4.01256806e-12 |          1.52260904e-16 |              2.91525107e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one-center       | 4.93448019e-12 | 1.72730347e-16 | 3.97915034e-12 |          1.15760067e-16 |              4.68729924e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt-all-h0-minus | 9.13244551e-12 | 9.78492461e-17 | 4.38526992e-12 |          3.01684955e-17 |              4.13112136e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt-all-h0-plus  | 7.9239688e-12  | 8.60721e-17    | 3.08952863e-12 |          2.81213332e-17 |              3.91560473e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt-all-h1-minus | 1.59507214e-12 | 1.25794557e-16 | 1.42985623e-12 |          2.07535297e-17 |              5.95433213e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt-all-h1-plus  | 7.90203073e-12 | 2.19008839e-16 | 2.93787217e-12 |          2.41614171e-17 |              6.1081211e-15  | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt-alt-h0-minus | 7.19516945e-12 | 1.12228477e-16 | 2.23987495e-12 |          2.61950984e-17 |              9.48499243e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt-alt-h0-plus  | 1.37647646e-12 | 1.27719016e-16 | 1.82187598e-12 |          2.20083501e-17 |              4.70534948e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt-alt-h1-minus | 7.95150892e-12 | 1.66004905e-16 | 3.06787928e-12 |          2.25130509e-17 |              4.9885561e-15  | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt-alt-h1-plus  | 5.78596104e-12 | 5.97666448e-17 | 2.79554158e-13 |          3.11675257e-17 |              3.58164421e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt-center       | 5.15464245e-13 | 8.4350929e-17  | 1.06303855e-12 |          2.43281275e-17 |              3.15235819e-15 | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one-all-h0-minus | 1.5404258e-12  | 2.80320472e-16 | 2.22011298e-12 |          1.41282759e-16 |              4.59220204e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one-all-h0-plus  | 5.47707441e-13 | 1.57642996e-16 | 7.38187289e-13 |          1.42938099e-16 |              4.34338605e-15 | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one-all-h1-minus | 8.85966186e-13 | 2.18358318e-16 | 1.26765265e-12 |          1.17424783e-16 |              3.78980488e-15 | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one-all-h1-plus  | 1.25939995e-12 | 1.9858518e-16  | 1.87982963e-12 |          1.67936295e-16 |              2.79619057e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one-alt-h0-minus | 5.70402097e-13 | 1.10669937e-16 | 7.71382958e-13 |          1.30889356e-16 |              7.51825591e-15 | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one-alt-h0-plus  | 1.47942487e-12 | 1.75857592e-16 | 2.12108109e-12 |          1.19257949e-16 |              2.82859956e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one-alt-h1-minus | 1.26243907e-12 | 1.87295925e-16 | 1.88404847e-12 |          1.32714928e-16 |              4.65203905e-15 | False               | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one-alt-h1-plus  | 8.7180404e-13  | 1.15847002e-16 | 1.24567023e-12 |          1.98973377e-16 |              3.23591099e-15 | True                | True     |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one-center       | 1.13000012e-12 | 1.83880688e-16 | 1.66633374e-12 |          1.55602564e-16 |              2.90893276e-15 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt-all-h0-minus | 2.65086347e-13 | 1.30944517e-16 | 9.60520552e-12 |          8.12015897e-18 |              2.92424629e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt-all-h0-plus  | 1.87075155e-13 | 2.21028165e-16 | 7.6840756e-12  |          5.25030185e-18 |              1.68123171e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt-all-h1-minus | 2.66076359e-13 | 8.24942328e-17 | 9.65272307e-12 |          5.51492393e-18 |              1.43820708e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt-all-h1-plus  | 2.65880796e-13 | 4.90601483e-17 | 9.63518154e-12 |          7.28154289e-18 |              1.3157082e-14  | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt-alt-h0-minus | 1.82000817e-13 | 1.51517254e-16 | 7.49178497e-12 |          5.04817668e-18 |              9.11081035e-15 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt-alt-h0-plus  | 2.65348832e-13 | 1.48589908e-16 | 9.62163682e-12 |          6.45293172e-18 |              1.09288552e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt-alt-h1-minus | 2.65904649e-13 | 2.1343875e-16  | 9.63806812e-12 |          6.00041116e-18 |              1.30886436e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt-alt-h1-plus  | 2.66139324e-13 | 1.68837383e-16 | 9.6493924e-12  |          5.74000861e-18 |              2.07929538e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt-center       | 2.66148946e-13 | 1.54281969e-16 | 9.65583169e-12 |          5.62679538e-18 |              2.75681674e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one-all-h0-minus | 3.00443074e-13 | 2.71741722e-16 | 5.45630208e-12 |          6.39402031e-17 |              8.89034178e-15 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one-all-h0-plus  | 1.60769957e-13 | 1.64256629e-16 | 8.03290767e-12 |          8.86091797e-17 |              5.78844329e-15 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one-all-h1-minus | 1.20762856e-13 | 1.59377719e-16 | 6.25233199e-12 |          7.28908282e-17 |              8.80695284e-15 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one-all-h1-plus  | 4.39818497e-13 | 1.13177154e-16 | 3.5005332e-13  |          6.87297701e-17 |              1.14053554e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one-alt-h0-minus | 3.67083859e-13 | 1.51002258e-16 | 3.92041954e-12 |          5.14660666e-17 |              1.00439185e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one-alt-h0-plus  | 4.15768128e-13 | 1.10825791e-16 | 6.9214634e-12  |          8.43849445e-17 |              1.01906469e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one-alt-h1-minus | 4.39380276e-13 | 1.45012041e-16 | 6.77002898e-12 |          6.59115711e-17 |              6.43021954e-15 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one-alt-h1-plus  | 2.21905827e-13 | 1.76452633e-16 | 4.94160268e-12 |          6.05468276e-17 |              1.07152985e-14 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one-center       | 1.15023083e-13 | 1.84951338e-16 | 5.89650551e-12 |          8.77608076e-17 |              7.55225239e-15 | True                | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt-all-h0-minus | 3.43863366e-12 | 2.46107117e-16 | 5.71009906e-12 |          6.38761723e-18 |              1.46317869e-14 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt-all-h0-plus  | 3.40091591e-12 | 1.53468818e-16 | 5.66080516e-12 |          5.41447427e-18 |              1.22707268e-14 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt-all-h1-minus | 3.42944558e-12 | 1.06224708e-16 | 5.70277159e-12 |          6.44735564e-18 |              1.07467534e-14 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt-all-h1-plus  | 3.41801904e-12 | 1.86238828e-16 | 5.68833869e-12 |          5.64298185e-18 |              1.62912023e-14 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt-alt-h0-minus | 3.41600766e-12 | 1.48833853e-16 | 5.6838978e-12  |          6.00789049e-18 |              2.19268044e-14 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt-alt-h0-plus  | 3.43006843e-12 | 9.67650439e-17 | 5.70277159e-12 |          6.29195904e-18 |              1.44659352e-14 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt-alt-h1-minus | 3.42193843e-12 | 2.01986865e-16 | 5.69055914e-12 |          4.86337079e-18 |              1.34217208e-14 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt-alt-h1-plus  | 3.42610871e-12 | 6.32631968e-17 | 5.69988501e-12 |          6.21185365e-18 |              9.62567485e-15 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt-center       | 3.42412261e-12 | 1.47620902e-16 | 5.69788661e-12 |          7.21643911e-18 |              1.07290267e-14 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one-all-h0-minus | 1.07366263e-11 | 1.3229977e-16  | 5.66515723e-11 |          6.15037757e-17 |              6.81715641e-15 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one-all-h0-plus  | 1.15593421e-11 | 1.12702816e-16 | 6.08444406e-11 |          5.47900979e-17 |              8.33879284e-15 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one-all-h1-minus | 1.09830659e-11 | 2.6191614e-16  | 5.79623016e-11 |          4.0035485e-17  |              5.05528788e-15 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one-all-h1-plus  | 1.10161237e-11 | 3.03840883e-16 | 5.81388271e-11 |          4.90615711e-17 |              7.77509033e-15 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one-alt-h0-minus | 1.06521527e-11 | 1.30050051e-16 | 5.62834224e-11 |          4.75894815e-17 |              6.23118517e-15 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one-alt-h0-plus  | 1.07708455e-11 | 2.03613168e-16 | 5.68347591e-11 |          5.6956456e-17  |              6.5411811e-15  | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one-alt-h1-minus | 1.10203568e-11 | 1.08122062e-16 | 5.81652504e-11 |          5.49406762e-17 |              4.30871063e-15 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one-alt-h1-plus  | 1.09890101e-11 | 2.94842005e-16 | 5.79876147e-11 |          6.35557353e-17 |              7.22203005e-15 | False               | True     |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one-center       | 1.10308891e-11 | 9.29703363e-17 | 5.8207883e-11  |          6.10823001e-17 |              1.04643391e-14 | False               | True     |

## 首例旧新指标

旧粗细诊断保留，新指标为(abs(R_f_plus−R_v_plus)加abs(R_f_minus−R_v_minus))/(2h)，另加两端各1e-12底限。带底限值不得超过原导数允许误差的十分之一；允许误差仍为1e-5加1e-3乘细档差分绝对值。

|   U_fv_with_floor |        U_limit |   old_CF_diagnostic | old_parent_verdict_changed   | passed   |
|------------------:|---------------:|--------------------:|:-----------------------------|:---------|
|    1.00138778e-08 | 1.14607546e-05 |      2.95031357e-05 | False                        | True     |

旧首例风险变化门仍不通过；若新首例通过，只说明按修订合同的最终fine稳定性取得资格，不回写旧判定。

## 隐式导数与细档稳定性

g_f与g_v均在相应中心独立核对H、混合偏导与Hv=g。逐维稳定性允许误差保持1e-6加1e-3乘两者最大绝对值。P与T-P共享任务梯度，分别加或不加软惩罚，G使用自己的匿名资产。

| point   | arm   | state   |   checks |    H_error_max |   linear_residual_max |   condition_max |   mixed_VJP_max |
|:--------|:------|:--------|---------:|---------------:|----------------------:|----------------:|----------------:|
| alt     | D-G   | f       |        6 | 5.36293419e-15 |        1.67400888e-13 |   326541.944    |  7.33857419e-14 |
| alt     | D-G   | v       |        6 | 6.235942e-15   |        1.05484344e-13 |   326541.944    |  2.9365399e-14  |
| alt     | D-P   | f       |        6 | 2.6920846e-15  |        1.07135619e-13 |   286494.924    |  2.27873276e-14 |
| alt     | D-P   | v       |        6 | 5.8519856e-15  |        8.93805376e-14 |   286494.925    |  1.04360964e-13 |
| one     | D-G   | f       |        6 | 2.44005638e-15 |        9.59970729e-15 |      803.919379 |  8.38440428e-13 |
| one     | D-G   | v       |        6 | 2.61811081e-15 |        8.23669702e-15 |      803.91938  |  4.68958206e-13 |
| one     | D-P   | f       |        6 | 1.79992502e-15 |        7.53643077e-15 |      677.328408 |  1.42108547e-13 |
| one     | D-P   | v       |        6 | 1.60222331e-15 |        7.34935086e-15 |      677.32841  |  6.25277607e-13 |

| role_id                          | arm   | point   |         Q_f |         Q_v |     gradient_f |     gradient_v |
|:---------------------------------|:------|:--------|------------:|------------:|---------------:|---------------:|
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one     | 0.62376227  | 0.62376227  | 5.86314851e-15 | 1.51300413e-16 |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one     | 0.620830055 | 0.620830055 | 2.48104488e-14 | 7.98379375e-17 |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one     | 1.10650425  | 1.10650426  | 1.99818498e-11 | 7.34004871e-17 |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one     | 1.35634692  | 1.35634693  | 2.05643509e-11 | 7.89299182e-17 |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one     | 0.90209113  | 0.90209113  | 1.13000012e-12 | 1.83880688e-16 |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one     | 0.787992554 | 0.787992554 | 4.93448019e-12 | 1.72730347e-16 |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one     | 0.785234562 | 0.785234562 | 1.06641258e-13 | 2.63298498e-16 |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one     | 0.601116762 | 0.601116762 | 1.82676357e-13 | 1.59459035e-16 |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one     | 1.47457405  | 1.47457405  | 2.8185787e-14  | 6.4401609e-17  |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one     | 1.6259673   | 1.6259673   | 3.20960706e-14 | 4.42354486e-17 |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one     | 1.15048494  | 1.15048494  | 1.10308891e-11 | 9.29703363e-17 |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one     | 0.887462775 | 0.887462775 | 1.15023083e-13 | 1.84951338e-16 |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt     | 0.618657942 | 0.618657942 | 3.84171861e-14 | 1.51788304e-16 |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt     | 0.614624782 | 0.614624782 | 5.28534464e-14 | 1.76399693e-16 |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt     | 0.163645167 | 0.163645167 | 5.49930369e-12 | 9.76053006e-17 |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt     | 0.164952109 | 0.164952109 | 6.25841161e-12 | 8.63024929e-17 |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt     | 0.937085096 | 0.937085096 | 5.15464245e-13 | 8.4350929e-17  |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt     | 0.906573251 | 0.906573251 | 1.79429713e-13 | 1.02348685e-16 |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt     | 1.03676687  | 1.03676687  | 5.17761832e-13 | 6.98226199e-17 |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt     | 0.800174483 | 0.800174483 | 3.32262429e-14 | 9.69886606e-17 |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt     | 1.73451959  | 1.73451959  | 1.92019794e-14 | 1.17527515e-16 |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt     | 1.78593104  | 1.78593104  | 6.64982392e-14 | 8.48930301e-17 |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt     | 1.31245002  | 1.31245002  | 3.42412261e-12 | 1.47620902e-16 |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt     | 1.31153232  | 1.31153232  | 2.66148946e-13 | 1.54281969e-16 |

## 固定差分结果

方向仍为全同向与交替两个单位方向，h仍为1e-4和3e-5，q点仍为1和交替0.9／1.1。两步长一致性、f/v差分稳定性和隐式一致性均按冻结门核对。信号不足记未决，不根据微小正负号放行。

| point   | arm   |   checks |   passed |       U_fv_max |   implicit_f_error_max |   implicit_v_error_max |   identifiable |
|:--------|:------|---------:|---------:|---------------:|-----------------------:|-----------------------:|---------------:|
| alt     | D-G   |       24 |       24 | 1.28782059e-06 |         1.28138983e-07 |         4.84882867e-08 |             24 |
| alt     | D-P   |       24 |       24 | 2.23185171e-07 |         1.64502804e-07 |         7.48906945e-08 |             24 |
| one     | D-G   |       24 |       24 | 0.000204547254 |         0.000339226559 |         0.000367835976 |             24 |
| one     | D-P   |       24 |       24 | 0.000407475384 |         0.000429745481 |         0.000432856747 |             24 |

| role_id                          | arm   | point   | direction   |      h |             D_f |             D_v |   U_fv_with_floor |        U_limit |   implicit_f_error |   derivative_limit | passed   | failed_gates   |
|:---------------------------------|:------|:--------|:------------|-------:|----------------:|----------------:|------------------:|---------------:|-------------------:|-------------------:|:---------|:---------------|
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one     | all         | 0.0001 |   0.104607546   |   0.104607546   |    1.00138778e-08 | 1.14607546e-05 |     4.99444952e-09 |     0.000114607546 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one     | all         | 3e-05  |   0.104607551   |   0.104607551   |    3.3381443e-08  | 1.14607551e-05 |     4.77322099e-10 |     0.000114607551 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one     | alt         | 0.0001 |   0.193269529   |   0.193269529   |    1.00521805e-08 | 2.03269529e-05 |     1.24297483e-07 |     0.000203269529 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | one     | alt         | 3e-05  |   0.193269416   |   0.193269416   |    3.34443556e-08 | 2.03269416e-05 |     1.11870357e-08 |     0.000203269416 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one     | all         | 0.0001 |   0.104020786   |   0.104020786   |    1.00283107e-08 | 1.14020786e-05 |     5.17094073e-09 |     0.000114020786 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one     | all         | 3e-05  |   0.10402079    |   0.10402079    |    3.3431403e-08  | 1.1402079e-05  |     4.6248487e-10  |     0.00011402079  | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one     | alt         | 0.0001 |   0.183201884   |   0.183201884   |    1.00210942e-08 | 1.93201884e-05 |     1.41286672e-07 |     0.000193201884 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | one     | alt         | 3e-05  |   0.183201755   |   0.183201755   |    3.34369541e-08 | 1.93201755e-05 |     1.2684358e-08  |     0.000193201755 | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one     | all         | 0.0001 | -77.8519154     | -77.8519318     |    0.000104217231 | 0.00778619154  |     0.000181163726 |     0.0778619154   | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one     | all         | 3e-05  | -77.8520975     | -77.8520824     |    0.000386868682 | 0.00778620975  |     9.72966745e-07 |     0.0778620975   | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one     | alt         | 0.0001 | -39.4614816     | -39.4614789     |    0.000108653328 | 0.00394714816  |     0.000429745481 |     0.0394714816   | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | one     | alt         | 3e-05  | -39.4618523     | -39.4618728     |    0.000407475384 | 0.00394718523  |     5.90221301e-05 |     0.0394718523   | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one     | all         | 0.0001 | -68.4478071     | -68.4477856     |    7.70445654e-05 | 0.00684578071  |     0.000242063865 |     0.0684578071   | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one     | all         | 3e-05  | -68.4477515     | -68.4475863     |    0.000204547254 | 0.00684577515  |     0.00018646944  |     0.0684577515   | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one     | alt         | 0.0001 | -35.0394315     | -35.0394035     |    5.89087603e-05 | 0.00350494315  |     0.000339226559 |     0.0350494315   | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | one     | alt         | 3e-05  | -35.0396827     | -35.0397382     |    0.000126089081 | 0.00350496827  |     8.80717398e-05 |     0.0350496827   | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one     | all         | 0.0001 |  -0.335364294   |  -0.335364287   |    2.47915014e-08 | 3.45364294e-05 |     1.58922271e-07 |     0.000345364294 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one     | all         | 3e-05  |  -0.335364428   |  -0.335364438   |    8.57913712e-08 | 3.45364428e-05 |     2.51898016e-08 |     0.000345364428 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one     | alt         | 0.0001 |   0.237402914   |   0.237402907   |    2.44623202e-08 | 2.47402914e-05 |     5.78983655e-09 |     0.000247402914 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | one     | alt         | 3e-05  |   0.237402897   |   0.237402908   |    8.54953118e-08 | 2.47402897e-05 |     1.07460102e-08 |     0.000247402897 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one     | all         | 0.0001 |   0.534475957   |   0.534475955   |    4.98897582e-08 | 5.44475957e-05 |     9.97019791e-07 |     0.000544475957 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one     | all         | 3e-05  |   0.534476866   |   0.534476864   |    1.65990182e-07 | 5.44476866e-05 |     8.81682785e-08 |     0.000544476866 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one     | alt         | 0.0001 |  -0.579938999   |  -0.579938998   |    4.98797662e-08 | 5.89938999e-05 |     8.91506887e-07 |     0.000589938999 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | one     | alt         | 3e-05  |  -0.579939812   |  -0.579939811   |    1.66025339e-07 | 5.89939812e-05 |     7.90819444e-08 |     0.000589939812 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one     | all         | 0.0001 |  -0.765491509   |  -0.76549151    |    3.00633954e-08 | 7.75491509e-05 |     3.56099722e-06 |     0.000775491509 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one     | all         | 3e-05  |  -0.765488268   |  -0.765488269   |    1.00189114e-07 | 7.75488268e-05 |     3.20204035e-07 |     0.000775488268 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one     | alt         | 0.0001 |   0.901441119   |   0.90144112    |    3.00528483e-08 | 9.11441119e-05 |     3.49557274e-06 |     0.000911441119 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | one     | alt         | 3e-05  |   0.901437938   |   0.901437938   |    1.00298285e-07 | 9.11437938e-05 |     3.14208308e-07 |     0.000911437938 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one     | all         | 0.0001 |   0.0951840987  |   0.0951840999  |    1.24363844e-08 | 1.05184099e-05 |     7.10457088e-06 |     0.000105184099 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one     | all         | 3e-05  |   0.0951905641  |   0.095190564   |    4.48667002e-08 | 1.05190564e-05 |     6.39187652e-07 |     0.000105190564 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one     | alt         | 0.0001 |  -0.202323392   |  -0.202323393   |    1.25102143e-08 | 2.12323392e-05 |     6.94279791e-06 |     0.000212323392 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | one     | alt         | 3e-05  |  -0.20232971    |  -0.20232971    |    4.47482764e-08 | 2.1232971e-05  |     6.24721111e-07 |     0.00021232971  | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one     | all         | 0.0001 |  -0.812783313   |  -0.812783313   |    1.06949996e-08 | 8.22783313e-05 |     1.15015085e-06 |     0.000822783313 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one     | all         | 3e-05  |  -0.812782266   |  -0.812782266   |    3.56907069e-08 | 8.22782266e-05 |     1.03553601e-07 |     0.000822782266 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one     | alt         | 0.0001 |   1.53904878    |   1.53904878    |    1.07005507e-08 | 0.000154904878 |     9.6846107e-07  |     0.00154904878  | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | one     | alt         | 3e-05  |   1.5390479     |   1.5390479     |    3.5616692e-08  | 0.00015490479  |     8.71708443e-08 |     0.0015490479   | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one     | all         | 0.0001 |  -0.55977447    |  -0.55977447    |    1.04640732e-08 | 5.6977447e-05  |     4.1249813e-07  |     0.00056977447  | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one     | all         | 3e-05  |  -0.559774846   |  -0.559774846   |    3.49579597e-08 | 5.69774846e-05 |     3.70580805e-08 |     0.000569774846 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one     | alt         | 0.0001 |   1.31283835    |   1.31283835    |    1.05051515e-08 | 0.000132283835 |     8.26387546e-07 |     0.00132283835  | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | one     | alt         | 3e-05  |   1.3128391     |   1.3128391     |    3.4924653e-08  | 0.00013228391  |     7.43187687e-08 |     0.0013228391   | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one     | all         | 0.0001 |   0.872041013   |   0.872040992   |    5.97480065e-07 | 8.82041013e-05 |     1.12430645e-06 |     0.000882041013 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one     | all         | 3e-05  |   0.872042037   |   0.872042034   |    1.96835215e-06 | 8.82042037e-05 |     1.00441756e-07 |     0.000882042037 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one     | alt         | 0.0001 |  -0.853971738   |  -0.853971741   |    5.75590907e-07 | 8.63971738e-05 |     1.24884015e-06 |     0.000863971738 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | one     | alt         | 3e-05  |  -0.853972877   |  -0.853972874   |    1.96921442e-06 | 8.63972877e-05 |     1.09548523e-07 |     0.000863972877 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one     | all         | 0.0001 |   2.19843956    |   2.19843957    |    7.74460487e-08 | 0.000220843956 |     3.8215196e-07  |     0.00220843956  | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one     | all         | 3e-05  |   2.19843931    |   2.19843921    |    1.43373088e-07 | 0.000220843931 |     1.33956792e-07 |     0.00220843931  | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one     | alt         | 0.0001 |  -1.95341418    |  -1.95341417    |    6.42094147e-08 | 0.000196341418 |     7.63827333e-07 |     0.00196341418  | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | one     | alt         | 3e-05  |  -1.95341345    |  -1.95341348    |    2.28527194e-07 | 0.000196341345 |     3.70464759e-08 |     0.00196341345  | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt     | all         | 0.0001 |  -0.0543558353  |  -0.0543558353  |    1.004996e-08   | 6.43558353e-06 |     6.99643676e-11 |     6.43558353e-05 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt     | all         | 3e-05  |  -0.0543558354  |  -0.0543558354  |    3.34924653e-08 | 6.43558354e-06 |     9.0465066e-12  |     6.43558354e-05 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt     | alt         | 0.0001 |  -0.0332576809  |  -0.0332576809  |    1.00538458e-08 | 4.32576809e-06 |     1.02588815e-09 |     4.32576809e-05 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-P   | alt     | alt         | 3e-05  |  -0.0332576799  |  -0.03325768    |    3.35165201e-08 | 4.32576799e-06 |     9.1265405e-11  |     4.32576799e-05 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt     | all         | 0.0001 |  -0.0565906767  |  -0.0565906767  |    1.00821565e-08 | 6.65906767e-06 |     6.5478109e-11  |     6.65906767e-05 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt     | all         | 3e-05  |  -0.0565906768  |  -0.0565906768  |    3.35960861e-08 | 6.65906768e-06 |     2.09342543e-11 |     6.65906768e-05 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt     | alt         | 0.0001 |  -0.0370237485  |  -0.0370237485  |    1.00743849e-08 | 4.70237485e-06 |     9.9305604e-10  |     4.70237485e-05 | True     | []             |
| main/f0/shadowsocks/G0/i1/trojan | D-G   | alt     | alt         | 3e-05  |  -0.0370237476  |  -0.0370237476  |    3.35868343e-08 | 4.70237476e-06 |     1.25416746e-10 |     4.70237476e-05 | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt     | all         | 0.0001 |  -0.0841611391  |  -0.0841611724  |    4.32966987e-08 | 9.41611391e-06 |     4.16677185e-08 |     9.41611391e-05 | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt     | all         | 3e-05  |  -0.0841612367  |  -0.0841611043  |    1.65698748e-07 | 9.41612367e-06 |     1.39175554e-07 |     9.41612367e-05 | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt     | alt         | 0.0001 |   0.0200591367  |   0.0200591687  |    4.89924204e-08 | 3.00591367e-06 |     3.43028896e-08 |     3.00591367e-05 | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-P   | alt     | alt         | 3e-05  |   0.0200593355  |   0.0200591708  |    1.98080253e-07 | 3.00593355e-06 |     1.64502804e-07 |     3.00593355e-05 | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt     | all         | 0.0001 |  -0.060679956   |  -0.0606799594  |    3.85595666e-07 | 7.0679956e-06  |     4.2480606e-08  |     7.0679956e-05  | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt     | all         | 3e-05  |  -0.0606799146  |  -0.0606799178  |    1.28772159e-06 | 7.06799146e-06 |     1.06373603e-09 |     7.06799146e-05 | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt     | alt         | 0.0001 |   0.00860680346 |   0.00860680228 |    3.86099152e-07 | 1.86068035e-06 |     8.82567047e-09 |     1.86068035e-05 | True     | []             |
| main/f0/shadowsocks/G2/i1/trojan | D-G   | alt     | alt         | 3e-05  |   0.0086068125  |   0.00860681137 |    1.28782059e-06 | 1.86068125e-06 |     2.15800811e-10 |     1.86068125e-05 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt     | all         | 0.0001 |  -0.0181896612  |  -0.0181896548  |    4.73739928e-08 | 2.81896612e-06 |     1.16957221e-08 |     2.81896612e-05 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt     | all         | 3e-05  |  -0.0181895772  |  -0.01818965    |    1.06128807e-07 | 2.81895772e-06 |     7.23564875e-08 |     2.81895772e-05 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt     | alt         | 0.0001 |  -0.0623648894  |  -0.0623648691  |    3.03087547e-08 | 7.23648894e-06 |     1.37106578e-08 |     7.23648894e-05 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-P   | alt     | alt         | 3e-05  |  -0.0623649215  |  -0.0623648751  |    8.91238907e-08 | 7.23649215e-06 |     4.58862163e-08 |     7.23649215e-05 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt     | all         | 0.0001 |  -0.171129348   |  -0.171129331   |    3.61451971e-08 | 1.81129348e-05 |     2.62304169e-08 |     0.000181129348 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt     | all         | 3e-05  |  -0.171129435   |  -0.171129322   |    2.14031382e-07 | 1.81129435e-05 |     1.13719507e-07 |     0.000181129435 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt     | alt         | 0.0001 |   0.0522827423  |   0.0522827357  |    3.28406183e-08 | 6.22827423e-06 |     1.93967086e-08 |     6.22827423e-05 | True     | []             |
| main/f0/vless/G1/i1/shadowsocks  | D-G   | alt     | alt         | 3e-05  |   0.0522828511  |   0.0522827241  |    2.3467598e-07  | 6.22828511e-06 |     1.28138983e-07 |     6.22828511e-05 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt     | all         | 0.0001 |   0.0847168341  |   0.0847168338  |    1.4753975e-08  | 9.47168341e-06 |     4.9525142e-09  |     9.47168341e-05 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt     | all         | 3e-05  |   0.0847168388  |   0.0847168386  |    4.78291453e-08 | 9.47168388e-06 |     2.52570062e-10 |     9.47168388e-05 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt     | alt         | 0.0001 |   0.0276493458  |   0.0276493426  |    1.32152059e-08 | 3.76493458e-06 |     1.52857481e-08 |     3.76493458e-05 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-P   | alt     | alt         | 3e-05  |   0.0276493311  |   0.0276493316  |    4.81437085e-08 | 3.76493311e-06 |     5.86395224e-10 |     3.76493311e-05 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt     | all         | 0.0001 |  -0.186163808   |  -0.186163808   |    1.40162318e-08 | 1.96163808e-05 |     1.80333154e-09 |     0.000196163808 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt     | all         | 3e-05  |  -0.18616381    |  -0.18616381    |    4.67355756e-08 | 1.9616381e-05  |     1.97208888e-10 |     0.00019616381  | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt     | alt         | 0.0001 |  -0.109935993   |  -0.109935993   |    1.40195625e-08 | 1.19935993e-05 |     5.7459108e-09  |     0.000119935993 | True     | []             |
| main/f0/trojan/G0/i1/shadowsocks | D-G   | alt     | alt         | 3e-05  |  -0.109935999   |  -0.109935999   |    4.67411267e-08 | 1.19935999e-05 |     4.8419381e-10  |     0.000119935999 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt     | all         | 0.0001 |   0.215453288   |   0.215453288   |    1.11701751e-08 | 2.25453288e-05 |     3.96047017e-09 |     0.000225453288 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt     | all         | 3e-05  |   0.215453292   |   0.215453292   |    3.72524206e-08 | 2.25453292e-05 |     3.23009453e-10 |     0.000225453292 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt     | alt         | 0.0001 |   0.123215376   |   0.123215376   |    1.11823875e-08 | 1.33215376e-05 |     3.20436788e-09 |     0.000133215376 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-P   | alt     | alt         | 3e-05  |   0.123215373   |   0.123215373   |    3.73486399e-08 | 1.33215373e-05 |     2.70788586e-10 |     0.000133215373 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt     | all         | 0.0001 |   0.215644433   |   0.215644433   |    1.01298961e-08 | 2.25644433e-05 |     4.05023237e-11 |     0.000225644433 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt     | all         | 3e-05  |   0.215644433   |   0.215644433   |    3.37330136e-08 | 2.25644433e-05 |     2.05863104e-13 |     0.000225644433 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt     | alt         | 0.0001 |   0.0526733616  |   0.0526733615  |    1.0134337e-08  | 6.26733616e-06 |     1.46738732e-09 |     6.26733616e-05 | True     | []             |
| main/f0/trojan/G2/i1/shadowsocks | D-G   | alt     | alt         | 3e-05  |   0.052673363   |   0.0526733629  |    3.37367144e-08 | 6.2673363e-06  |     8.25691321e-11 |     6.2673363e-05  | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt     | all         | 0.0001 |  -0.246721128   |  -0.246721128   |    6.68545211e-08 | 2.56721128e-05 |     2.5983744e-08  |     0.000256721128 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt     | all         | 3e-05  |  -0.246721105   |  -0.246721104   |    2.23185171e-07 | 2.56721105e-05 |     2.56951047e-09 |     0.000256721105 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt     | alt         | 0.0001 |   0.246203771   |   0.246203771   |    6.69333469e-08 | 2.56203771e-05 |     2.54486575e-08 |     0.000256203771 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-P   | alt     | alt         | 3e-05  |   0.246203748   |   0.246203747   |    2.23174069e-07 | 2.56203748e-05 |     2.417821e-09   |     0.000256203748 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt     | all         | 0.0001 |  -0.400464771   |  -0.400464761   |    9.64464056e-08 | 4.10464771e-05 |     5.809957e-08   |     0.000410464771 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt     | all         | 3e-05  |  -0.400464717   |  -0.400464717   |    3.5479841e-07  | 4.10464717e-05 |     4.70746453e-09 |     0.000410464717 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt     | alt         | 0.0001 |   0.631041296   |   0.631041285   |    9.5567109e-08  | 6.41041296e-05 |     5.37812475e-08 |     0.000641041296 | True     | []             |
| main/f0/vmess/G1/i1/shadowsocks  | D-G   | alt     | alt         | 3e-05  |   0.631041246   |   0.631041246   |    3.54791009e-07 | 6.41041246e-05 |     4.0906255e-09  |     0.000641041246 | True     | []             |

软惩罚继续使用独立解析oracle及激活分支核对。跨切换时普通完整中心差分的截断项单列，不误用作唯一验收标准。各臂f/v的完整分项记录保存于arm-FD-checks表。

## 阶段状态及停止路径

| stage       | executed   |   new_LR_fits | passed   |   permission_negatives |   reused_fine |   validation_steps |   centers |   checks | status                    |
|:------------|:-----------|--------------:|:---------|-----------------------:|--------------:|-------------------:|----------:|---------:|:--------------------------|
| first-three | True       |             0 | True     |                      3 |             3 |                  3 |       未执行或不适用 |      未执行或不适用 | 未执行或不适用                       |
| one         | True       |           未执行或不适用 | True     |                    未执行或不适用 |           未执行或不适用 |                未执行或不适用 |        12 |       48 | solution_one_qualified_v2 |
| alt         | True       |           未执行或不适用 | True     |                    未执行或不适用 |           未执行或不适用 |                未执行或不适用 |        12 |       48 | solution_alt_qualified_v2 |

无阶段异常；若资格门未过，见阶段状态和差分失败路径。

各点solve_log、fine_state、validation_log、validation_state分别使用明确schema，未把快照侧车缺少accepted字段解释为失败。失败或未决不启动后续依赖阶段，不轮换角色、步长或后端。

## 计算与权限账本

|   fine_states_created |   fine_states_reused |   formal_classifier_fits |   implicit_evaluations |   new_LR_accepted |   new_LR_attempted |   new_mapping_fits |   old_reference_refinements |   refinement_steps |   validation_steps |
|----------------------:|---------------------:|-------------------------:|-----------------------:|------------------:|-------------------:|-------------------:|----------------------------:|-------------------:|-------------------:|
|                   213 |                    3 |                        0 |                     48 |               202 |                202 |                  0 |                          11 |                426 |                216 |

完整上限为202个新LR、11个旧源内参照精炼、216次一次校验和48次中心隐式评估。当前表为实际计算量，f/v快照不是独立访问。已完成的旧计数、72位置几何与惩罚oracle仅来源复核，不重新拟合。

原父产物SHA保持不变，所有数值资产按源内白名单和P/G臂权限加载，G不加载P身份或映射。实际目标C/U/H数值读取0，PCAP读取0，新漂移映射0，正式分类器0。旧P-small正向结果及其身份归因边界未改。

## 结论与适用范围

完整预定源内先导在两个点、两个方向和两个步长上通过第二版数值验收，可据此制定正式业务比较；这不是动态系数的分类收益。

本修订是在已分析首例上形成，首例复核不称为独立盲测。即使完整先导通过，也仅覆盖固定六角色、两点和两方向，不证明全部q范围及未来元优化访问点可靠，不是外部验证。正式业务比较仍需独立合同、全矩阵预算和新q点的求解拒绝政策。

## 可复核产物

- [批准方案](F:/Program/VSCode/MyGit/ProxyAnalysis/plan/dynamic-soft-drift-implicit-fine-validation-v2-plan-20261012.md)
- [冻结合同](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-v2-20261012/run-01/manifests/contract.json)
- [完成状态](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-v2-20261012/run-01/completion.json)
- [独立校验表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-v2-20261012/run-01/validation-checks.parquet)
- [q为1差分表](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-v2-20261012/run-01/one-FD-checks.parquet)
- [实际计算账本](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-v2-20261012/run-01/ledger.json)
- [完整性验证](F:/Program/VSCode/MyGit/ProxyAnalysis/outputs/dynamic-soft-drift-implicit-v2-20261012/run-01/verification.json)
- [运行说明](F:/Program/VSCode/MyGit/ProxyAnalysis/eval/dynamic_soft_drift_implicit_v2/README.md)
