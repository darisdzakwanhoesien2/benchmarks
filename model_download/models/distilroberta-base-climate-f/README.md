---
language: en
license: apache-2.0
tags:
- climate
---

# Model Card for distilroberta-base-climate-f 

## Model Description

This is the ClimateBERT language model based on the FULL-SELECT sample selection strategy.

*Note: We generally recommend choosing this language model over those based on the other sample selection strategies (unless you have good reasons not to). This is also the only language model we will update from time to time.*

Using the [DistilRoBERTa](https://huggingface.co/distilroberta-base) model as starting point, the ClimateBERT Language Model is additionally pre-trained on a text corpus comprising climate-related research paper abstracts, corporate and general news and reports from companies. The underlying methodology can be found in our [language model research paper](https://arxiv.org/abs/2110.12010).

*Update September 2, 2022: Now additionally pre-trained on an even larger text corpus, comprising >2M paragraphs. If you are looking for the language model before the update (i.e. for reproducibility), just use an older commit like [6be4fbd](https://huggingface.co/climatebert/distilroberta-base-climate-f/tree/6be4fbd3fedfd78ccb3c730c1f166947fbc940ba).*

## Climate performance model card

| distilroberta-base-climate-f                                             |                |
|--------------------------------------------------------------------------|----------------|
| 1. Is the resulting model publicly available?                            | Yes            |
| 2. How much time does the training of the final model take?              | 48 hours        |
| 3. How much time did all experiments take (incl. hyperparameter search)? | 350 hours      |
| 4. What was the power of GPU and CPU?                                    | 0.7 kW         |
| 5. At which geo location were the computations performed?                | Germany        |
| 6. What was the energy mix at the geo location?                          | 470 gCO2eq/kWh |
| 7. How much CO2eq was emitted to train the final model?                  | 15.79 kg        |
| 8. How much CO2eq was emitted for all experiments?                       | 115.15 kg       |
| 9. What is the average CO2eq emission for the inference of one sample?   | 0.62 mg        |
| 10. Which positive environmental impact can be expected from this work?  | This work can be categorized as a building block tools following Jin et al (2021). It supports the training of NLP models in the field of climate change and, thereby, have a positive environmental impact in the future. |
| 11. Comments                                                             | Block pruning could decrease CO2eq emissions |

## Citation Information

```bibtex
@inproceedings{wkbl2022climatebert,
    title={{ClimateBERT: A Pretrained Language Model for Climate-Related Text}},
    author={Webersinke, Nicolas and Kraus, Mathias and Bingler, Julia and Leippold, Markus},
    booktitle={Proceedings of AAAI 2022 Fall Symposium: The Role of AI in Responding to Climate Challenges},
    year={2022},
    doi={https://doi.org/10.48550/arXiv.2212.13631},
}
```