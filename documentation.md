## Additional File Classifications

[
	{
		"file_path": "pages/3_ABSA_Classical.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for running classical ABSA model and visualizing results.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/0_0_ClimateBERT_5_Model_Deep_Explorer.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for deep exploration of ClimateBERT model results.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/esg_dashboard_new_Distribution Document.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Document-level dashboard for ESG sentiment and tone analysis.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/0_0_ClimateBERT_7_Full_Model_Visualization.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for full visualization of ClimateBERT models.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/0_0_2_Batch_Prediction.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for batch prediction using ClimateBERT models.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/esg_dashboard_new_0_Metric_Analysis.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for metric analysis comparing ground truth and predictions.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/esg_dashboard_new_01_Aspects_Raw.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for viewing raw aspect data before manual annotation.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/0_0_ClimateBERT_11_ClimateBERT_Parse_JSON.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for parsing and viewing ClimateBERT JSON results.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth_Windows.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for batch processing ClimateBERT ground truth (Windows).",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/0_0_ClimateBERT_4_Model_Analysis.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for analysis of ClimateBERT model performance and metrics.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	}
]
# Repository File Classification and Documentation Pipeline
https://chatgpt.com/c/69ae8427-adf8-8324-9e3e-b22aedc8fbae
This section provides a structured classification of all files in the repository, including their roles, descriptions, and recommended documentation prompts. Use this as a foundation for your documentation pipeline.

```
[
	{
		"file_path": "app.py",
		"file_type": "python",
		"category": "streamlit_app_core",
		"short_description": "Main entry point for the Streamlit ESG Scoring Dashboard app.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/1_Analyze.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for analyzing ESG-related text and displaying results.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "pages/ABSA_Model_Comparison.py",
		"file_type": "python",
		"category": "streamlit_page",
		"short_description": "Streamlit page for comparing ABSA models on input text.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "api/absa_client.py",
		"file_type": "python",
		"category": "api",
		"short_description": "Client for interacting with ABSA Hugging Face Space APIs.",
		"recommended_documentation_prompt": "api_documentation"
	},
	{
		"file_path": "api/climatebert_client.py",
		"file_type": "python",
		"category": "api",
		"short_description": "Client for interacting with ClimateBERT Hugging Face Space APIs.",
		"recommended_documentation_prompt": "api_documentation"
	},
	{
		"file_path": "services/inference.py",
		"file_type": "python",
		"category": "pipeline",
		"short_description": "Runs inference using Hugging Face pipelines.",
		"recommended_documentation_prompt": "pipeline_documentation"
	},
	{
		"file_path": "utils/data_loader.py",
		"file_type": "python",
		"category": "utility",
		"short_description": "Utility functions for loading and parsing ESG data.",
		"recommended_documentation_prompt": "code_documentation"
	},
	{
		"file_path": "utils/metrics.py",
		"file_type": "python",
		"category": "utility",
		"short_description": "Utility functions for computing evaluation metrics.",
		"recommended_documentation_prompt": "code_documentation"
	},
	{
		"file_path": "config/model_registry.py",
		"file_type": "python",
		"category": "configuration",
		"short_description": "Registry of available models and their metadata.",
		"recommended_documentation_prompt": "architecture_documentation"
	},
	{
		"file_path": "data/sentiment_ontology.json",
		"file_type": "json",
		"category": "dataset",
		"short_description": "Ontology mapping for sentiment labels and aliases.",
		"recommended_documentation_prompt": "dataset_documentation"
	},
	{
		"file_path": "ui/sidebar.py",
		"file_type": "python",
		"category": "streamlit_app_core",
		"short_description": "Sidebar component for model selection in Streamlit app.",
		"recommended_documentation_prompt": "streamlit_page_documentation"
	},
	{
		"file_path": "README.md",
		"file_type": "markdown",
		"category": "documentation",
		"short_description": "Project overview, setup instructions, and structure.",
		"recommended_documentation_prompt": "architecture_documentation"
	},
	{
		"file_path": "requirements.txt",
		"file_type": "text",
		"category": "configuration",
		"short_description": "Python dependencies for the project.",
		"recommended_documentation_prompt": "deployment_documentation"
	}
]
```
