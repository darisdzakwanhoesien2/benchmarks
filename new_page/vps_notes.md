1. Setup your VPS in VS Code -> so that you just need to enter your password
2. Download the model from https://drive.google.com/drive/u/1/folders/1jX_g98viQl4P-Q7lGwkvMmJ5whzJ2SVm and store it on model_download/models

/home/ubuntu/apps/benchmarks/new_page/pages/0_3_testing.py:366: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
/home/ubuntu/apps/benchmarks/new_page/pages/0_3_testing.py:366: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
Loading weights: 100%|███████████████████████████████████████████████████████████| 101/101 [00:00<00:00, 35891.27it/s]
RobertaForSequenceClassification LOAD REPORT from: /home/ubuntu/apps/benchmarks/model_download/models/distilroberta-base-climate-d
Key                             | Status     | 
--------------------------------+------------+-
lm_head.layer_norm.weight       | UNEXPECTED | 
lm_head.bias                    | UNEXPECTED | 
lm_head.layer_norm.bias         | UNEXPECTED | 
roberta.embeddings.position_ids | UNEXPECTED | 
lm_head.dense.bias              | UNEXPECTED | 
lm_head.dense.weight            | UNEXPECTED | 
classifier.dense.bias           | MISSING    | 
classifier.out_proj.weight      | MISSING    | 
classifier.dense.weight         | MISSING    | 
classifier.out_proj.bias        | MISSING    | 

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:      those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.
/home/ubuntu/apps/benchmarks/new_page/pages/0_3_testing.py:405: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.utcnow().isoformat(),
/home/ubuntu/apps/benchmarks/new_page/pages/0_3_testing.py:405: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.utcnow().isoformat(),
Loading weights: 100%|████████████████████████████████████████████████████████████| 101/101 [00:00<00:00, 1420.75it/s]
RobertaForSequenceClassification LOAD REPORT from: /home/ubuntu/apps/benchmarks/model_download/models/distilroberta-base-climate-d-s
Key                             | Status     | 
--------------------------------+------------+-
lm_head.layer_norm.weight       | UNEXPECTED | 
lm_head.bias                    | UNEXPECTED | 
lm_head.layer_norm.bias         | UNEXPECTED | 
roberta.embeddings.position_ids | UNEXPECTED | 
lm_head.dense.bias              | UNEXPECTED | 
lm_head.dense.weight            | UNEXPECTED | 
classifier.dense.bias           | MISSING    | 
classifier.out_proj.weight      | MISSING    | 
classifier.dense.weight         | MISSING    | 
classifier.out_proj.bias        | MISSING    | 

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:      those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.