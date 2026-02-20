# 📦 Project Directory Structure

**Root:** `/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/esg_project/benchmarks`

  📄 .DS_Store<br>
  📄 .env<br>
  📄 .gitignore<br>
  📄 README.md<br>
<details><summary>📁 api/</summary>
    📄 absa_client.py<br>
    📄 climatebert_client.py<br>
    📄 climatebert_client_combined.py<br>
    📄 esgdata_client.py<br>
</details>
  📄 api_client.py<br>
  📄 app.py<br>
  📄 batch_predict.py<br>
<details><summary>📁 data/</summary>
    📄 .DS_Store<br>
    📄 climatebert_errors.log<br>
    📄 climatebert_parsed.json<br>
    📄 climatebert_results.json<br>
  <details><summary>📁 ground_truth/</summary>
      📄 absa_mapping.csv<br>
      📄 climatebert_parsed.json<br>
      📄 climatebert_results.json<br>
  </details>
  <details><summary>📁 ground_truth_windows/</summary>
      📄 absa_mapping.csv<br>
      📄 climatebert_parsed.json<br>
      📄 climatebert_results.json<br>
  </details>
    📄 history.json<br>
</details>
<details><summary>📁 pages/</summary>
    📄 0_0_1_Single_Prediction.py<br>
    📄 0_0_2_Batch_Prediction.py<br>
    📄 0_0_3_Model_Explorer.py<br>
    📄 0_0_ClimateBERT_10_ClimateBERT_Multi_Model.py<br>
    📄 0_0_ClimateBERT_11_ClimateBERT_Parse_JSON.py<br>
    📄 0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py<br>
    📄 0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth_Windows.py<br>
    📄 0_0_ClimateBERT_4_Model_Analysis.py<br>
    📄 0_ESG_02_ESG_Preprocess.py<br>
    📄 0_ESG_03_ESG_Training.py<br>
    📄 0_ESG_04_ESG_Evaluation.py<br>
    📄 0_ESG_05_ESG_XAI.py<br>
    📄 0_ESG_06_ESG_Compare.py<br>
    📄 1_Analyze.py<br>
    📄 2_ABSA_Rule_Based.py<br>
    📄 3_ABSA_Classical.py<br>
    📄 5_ABSA_Deep_Learning.py<br>
</details>
  📄 project_directory.md<br>
  📄 requirements.txt<br>
  📄 structure_code.py<br>
  📄 test.py<br>
  📄 test_api.py<br>
<details><summary>📁 utils/</summary>
    📄 api_safe.py<br>
    📄 climatebert_analysis.py<br>
    📄 climatebert_batch.py<br>
    📄 climatebert_batch_core.py<br>
    📄 climatebert_batch_windows.py<br>
    📄 climatebert_groundtruth_storage.py<br>
    📄 climatebert_groundtruth_storage_windows.py<br>
    📄 climatebert_parser.py<br>
    📄 climatebert_storage.py<br>
    📄 climatebert_storage_windows.py<br>
    📄 dataframe.py<br>
    📄 error_logger.py<br>
    📄 file_handler.py<br>
    📄 formatter.py<br>
    📄 json_logger.py<br>
    📄 logger.py<br>
    📄 merge_climatebert_absa.py<br>
    📄 parse_climatebert_results.py<br>
    📄 save_climatebert_results.py<br>
    📄 visualization.py<br>
</details>