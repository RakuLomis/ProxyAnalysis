# Extend v3 证据索引

本索引引用实际存在的冻结记录；完整输入清单在本地 `evidence-review-01/audit.json`。本轮没有修改原始实验记录。

| 文件                                                                                                   | SHA256                                                           |
|:-------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------|
| outputs\extend-calibration-20260930\run-01\extraction-03\training-preparation-01\preregistration.json  | c18fc0b73ce33a23938f78d44998796b973c23a715afd564e6f07d742cb51683 |
| outputs\extend-calibration-20260930\run-01\extraction-03\formal-01\execution-contract.json             | 6c4802da991e3357505a91d985e30f3251e1bedb3ce17f9382221b2099f086d1 |
| outputs\extend-calibration-20260930\run-01\extraction-03\formal-01\execution-contract-revision-02.json | 3d7587272c6a93b2fbe10641cbcf877e97c06cd2f1613bfef599e34802680f40 |
| outputs\extend-calibration-20260930\run-01\extraction-03\formal-01\repair-02\compatibility.json        | 2d23991b1761fe45aba6562f33fde162c462d2175b73532dc55f698a3f010066 |
| outputs\extend-calibration-20260930\run-01\extraction-03\formal-01\generation-gate.json                | 3e3dc85f46ac6f74d920c5ff02a2769775104cc91367fae60fd68eeebf0de913 |
| outputs\extend-calibration-20260930\run-01\extraction-03\formal-01\restricted-prediction-seal.json     | 34ea412f1559ff8213c282fcadcc2ff2ad66d0cc768250f3c086678b7806f438 |
| outputs\extend-calibration-20260930\run-01\extraction-03\formal-01\reference-prediction-seal.json      | dc0b30713829dc68d5e3f19a648da9d9764c9f0088056651969cda13d6aa401a |
| outputs\extend-calibration-20260930\run-01\extraction-03\formal-01\statistics-complete.json            | a83dcd5cbce24e83e443e2cf88f183e30aadbe3061bc52bfcea89545f81b8dc6 |
| outputs\extend-calibration-20260930\run-01\extraction-03\formal-01\contrasts.parquet                   | fa337c0a082a807bd64f7d6d767638ebbbb87bd2863eecbf628fef647d8adaaa |
| outputs\extend-calibration-20260930\run-01\extraction-03\training-preparation-01\roles.parquet         | d8e2cc78a56a0d72e180eed92570f11537d392ac409af844d39d8ec8de5a14a2 |

## 核对结果

| 检查                                                  |   结果 |
|:------------------------------------------------------|-------:|
| models_predictions_and_source_hashes                  |   True |
| WT_shared_visits_roles_and_folds_identical            |   True |
| scenario_roles_and_new_business_permissions           |   True |
| full_six_class_F1_reconstructed                       |   4536 |
| saved_bootstrap_intervals_verified_without_resampling |   1512 |
| coverage_denominators_equal_frozen_W_features         |   True |
| all_reviewed_inputs_unchanged                         |   True |
