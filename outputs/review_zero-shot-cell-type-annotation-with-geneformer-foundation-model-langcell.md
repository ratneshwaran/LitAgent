## Executive summary

Reviewed 10 papers across 1 venues. We summarize methods, results, and limitations, and identify common gaps.

## Comparative matrix

| Paper | Venue | Year | Citations | Methods | Results | Limitations |
| --- | --- | --- | --- | --- | --- | --- |
| GenoHoption: Bridging Gene Network Graphs and Single-Cell Foundation
  Models | arXiv | 2024 |  |  |  |  |
| scInterpreter: Training Large Language Models to Interpret scRNA-seq
  Data for Cell Type Annotation | arXiv | 2024 |  |  |  |  |
| GRIT: Graph-Regularized Logit Refinement for Zero-shot Cell Type
  Annotation | arXiv | 2025 |  |  |  |  |
| ChromFound: Towards A Universal Foundation Model for Single-Cell
  Chromatin Accessibility Data | arXiv | 2025 |  |  |  |  |
| Fine-grained Multi-class Nuclei Segmentation with Molecular-empowered
  All-in-SAM Model | arXiv | 2025 |  |  |  |  |
| ZERO: Industry-ready Vision Foundation Model with Multi-modal Prompts | arXiv | 2025 |  |  |  |  |
| LangCell: Language-Cell Pre-training for Cell Identity Understanding | arXiv | 2024 |  |  |  |  |
| Efficient Fine-Tuning of Single-Cell Foundation Models Enables Zero-Shot
  Molecular Perturbation Prediction | arXiv | 2024 |  |  |  |  |
| Cell-ontology guided transcriptome foundation model | arXiv | 2024 |  |  |  |  |
| Segment Any Change | arXiv | 2024 |  |  |  |  |


## Mini-reviews

### GenoHoption: Bridging Gene Network Graphs and Single-Cell Foundation
  Models

arXiv, 2024, Jiabei Cheng; Jiachen Li; Kaiyuan Yang; Hongbin Shen; Ye Yuan

**TL;DR**

The remarkable success of foundation models has sparked growing interest in
their application to single-cell biology. Models like Geneformer and scGPT
promise to serve as versatile tools in this specialized field. However,
representing a cell as a sequence of genes remains an ope...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> The remarkable success of foundation models has sparked growing interest in
their application to single-cell biology. Models like Geneformer and scGPT
promise to serve as versatile tools in this speci (abstract)

### scInterpreter: Training Large Language Models to Interpret scRNA-seq
  Data for Cell Type Annotation

arXiv, 2024, Cong Li; Meng Xiao; Pengfei Wang; Guihai Feng; Xin Li; Yuanchun Zhou

**TL;DR**

Despite the inherent limitations of existing Large Language Models in
directly reading and interpreting single-cell omics data, they demonstrate
significant potential and flexibility as the Foundation Model. This research
focuses on how to train and adapt the Large Language Model...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Despite the inherent limitations of existing Large Language Models in
directly reading and interpreting single-cell omics data, they demonstrate
significant potential and flexibility as the Foundation (abstract)

### GRIT: Graph-Regularized Logit Refinement for Zero-shot Cell Type
  Annotation

arXiv, 2025, Tianxiang Hu; Chenyi Zhou; Jiaxiang Liu; Jiongxin Wang; Ruizhe Chen; Haoxiang Xia; Gaoang Wang; Jian Wu; Zuozhu Liu

**TL;DR**

Cell type annotation is a fundamental step in the analysis of single-cell RNA
sequencing (scRNA-seq) data. In practice, human experts often rely on the
structure revealed by principal component analysis (PCA) followed by
$k$-nearest neighbor ($k$-NN) graph construction to guide a...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Cell type annotation is a fundamental step in the analysis of single-cell RNA
sequencing (scRNA-seq) data. In practice, human experts often rely on the
structure revealed by principal component analys (abstract)

### ChromFound: Towards A Universal Foundation Model for Single-Cell
  Chromatin Accessibility Data

arXiv, 2025, Yifeng Jiao; Yuchen Liu; Yu Zhang; Xin Guo; Yushuai Wu; Chen Jiang; Jiyang Li; Hongwei Zhang; Limei Han; Xin Gao; Yuan Qi; Yuan Cheng

**TL;DR**

The advent of single-cell Assay for Transposase-Accessible Chromatin using
sequencing (scATAC-seq) offers an innovative perspective for deciphering
regulatory mechanisms by assembling a vast repository of single-cell chromatin
accessibility data. While foundation models have achi...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> The advent of single-cell Assay for Transposase-Accessible Chromatin using
sequencing (scATAC-seq) offers an innovative perspective for deciphering
regulatory mechanisms by assembling a vast repositor (abstract)

### Fine-grained Multi-class Nuclei Segmentation with Molecular-empowered
  All-in-SAM Model

arXiv, 2025, Xueyuan Li; Can Cui; Ruining Deng; Yucheng Tang; Quan Liu; Tianyuan Yao; Shunxing Bao; Naweed Chowdhury; Haichun Yang; Yuankai Huo

**TL;DR**

Purpose: Recent developments in computational pathology have been driven by
advances in Vision Foundation Models, particularly the Segment Anything Model
(SAM). This model facilitates nuclei segmentation through two primary methods:
prompt-based zero-shot segmentation and the use...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Purpose: Recent developments in computational pathology have been driven by
advances in Vision Foundation Models, particularly the Segment Anything Model
(SAM). This model facilitates nuclei segmentat (abstract)

### ZERO: Industry-ready Vision Foundation Model with Multi-modal Prompts

arXiv, 2025, Sangbum Choi; Kyeongryeol Go; Taewoong Jang

**TL;DR**

Foundation models have revolutionized AI, yet they struggle with zero-shot
deployment in real-world industrial settings due to a lack of high-quality,
domain-specific datasets. To bridge this gap, Superb AI introduces ZERO, an
industry-ready vision foundation model that leverages...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Foundation models have revolutionized AI, yet they struggle with zero-shot
deployment in real-world industrial settings due to a lack of high-quality,
domain-specific datasets. To bridge this gap, Sup (abstract)

### LangCell: Language-Cell Pre-training for Cell Identity Understanding

arXiv, 2024, Suyuan Zhao; Jiahuan Zhang; Yushuai Wu; Yizhen Luo; Zaiqing Nie

**TL;DR**

Cell identity encompasses various semantic aspects of a cell, including cell
type, pathway information, disease information, and more, which are essential
for biologists to gain insights into its biological characteristics.
Understanding cell identity from the transcriptomic data...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Cell identity encompasses various semantic aspects of a cell, including cell
type, pathway information, disease information, and more, which are essential
for biologists to gain insights into its biol (abstract)

### Efficient Fine-Tuning of Single-Cell Foundation Models Enables Zero-Shot
  Molecular Perturbation Prediction

arXiv, 2024, Sepideh Maleki; Jan-Christian Huetter; Kangway V. Chuang; David Richmond; Gabriele Scalia; Tommaso Biancalani

**TL;DR**

Predicting transcriptional responses to novel drugs provides a unique
opportunity to accelerate biomedical research and advance drug discovery
efforts. However, the inherent complexity and high dimensionality of cellular
responses, combined with the extremely limited available ex...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Predicting transcriptional responses to novel drugs provides a unique
opportunity to accelerate biomedical research and advance drug discovery
efforts. However, the inherent complexity and high dimens (abstract)

### Cell-ontology guided transcriptome foundation model

arXiv, 2024, Xinyu Yuan; Zhihao Zhan; Zuobai Zhang; Manqi Zhou; Jianan Zhao; Boyu Han; Yue Li; Jian Tang

**TL;DR**

Transcriptome foundation models TFMs hold great promises of deciphering the
transcriptomic language that dictate diverse cell functions by self-supervised
learning on large-scale single-cell gene expression data, and ultimately
unraveling the complex mechanisms of human diseases....

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Transcriptome foundation models TFMs hold great promises of deciphering the
transcriptomic language that dictate diverse cell functions by self-supervised
learning on large-scale single-cell gene expr (abstract)

### Segment Any Change

arXiv, 2024, Zhuo Zheng; Yanfei Zhong; Liangpei Zhang; Stefano Ermon

**TL;DR**

Visual foundation models have achieved remarkable results in zero-shot image
classification and segmentation, but zero-shot change detection remains an open
problem. In this paper, we propose the segment any change models (AnyChange), a
new type of change detection model that sup...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Visual foundation models have achieved remarkable results in zero-shot image
classification and segmentation, but zero-shot change detection remains an open
problem. In this paper, we propose the segm (abstract)

## Gaps & future work

- Few works report comparisons against strong baselines.
- Open-sourcing code and datasets
- Larger, diverse cohorts
- Robust baseline comparisons

### References

- Jiabei Cheng, Jiachen Li, Kaiyuan Yang, Hongbin Shen, Ye Yuan. (2024) GenoHoption: Bridging Gene Network Graphs and Single-Cell Foundation
  Models. arXiv. http://arxiv.org/abs/2411.06331v1
- Cong Li, Meng Xiao, Pengfei Wang, Guihai Feng, Xin Li, Yuanchun Zhou. (2024) scInterpreter: Training Large Language Models to Interpret scRNA-seq
  Data for Cell Type Annotation. arXiv. http://arxiv.org/abs/2402.12405v1
- Tianxiang Hu, Chenyi Zhou, Jiaxiang Liu, Jiongxin Wang, Ruizhe Chen, Haoxiang Xia, Gaoang Wang, Jian Wu, Zuozhu Liu. (2025) GRIT: Graph-Regularized Logit Refinement for Zero-shot Cell Type
  Annotation. arXiv. http://arxiv.org/abs/2508.04747v1
- Yifeng Jiao, Yuchen Liu, Yu Zhang, Xin Guo, Yushuai Wu, Chen Jiang, Jiyang Li, Hongwei Zhang, Limei Han, Xin Gao, Yuan Qi, Yuan Cheng. (2025) ChromFound: Towards A Universal Foundation Model for Single-Cell
  Chromatin Accessibility Data. arXiv. http://arxiv.org/abs/2505.12638v2
- Xueyuan Li, Can Cui, Ruining Deng, Yucheng Tang, Quan Liu, Tianyuan Yao, Shunxing Bao, Naweed Chowdhury, Haichun Yang, Yuankai Huo. (2025) Fine-grained Multi-class Nuclei Segmentation with Molecular-empowered
  All-in-SAM Model. arXiv. http://arxiv.org/abs/2508.15751v1
- Sangbum Choi, Kyeongryeol Go, Taewoong Jang. (2025) ZERO: Industry-ready Vision Foundation Model with Multi-modal Prompts. arXiv. http://arxiv.org/abs/2507.04270v3
- Suyuan Zhao, Jiahuan Zhang, Yushuai Wu, Yizhen Luo, Zaiqing Nie. (2024) LangCell: Language-Cell Pre-training for Cell Identity Understanding. arXiv. http://arxiv.org/abs/2405.06708v5
- Sepideh Maleki, Jan-Christian Huetter, Kangway V. Chuang, David Richmond, Gabriele Scalia, Tommaso Biancalani. (2024) Efficient Fine-Tuning of Single-Cell Foundation Models Enables Zero-Shot
  Molecular Perturbation Prediction. arXiv. http://arxiv.org/abs/2412.13478v2
- Xinyu Yuan, Zhihao Zhan, Zuobai Zhang, Manqi Zhou, Jianan Zhao, Boyu Han, Yue Li, Jian Tang. (2024) Cell-ontology guided transcriptome foundation model. arXiv. http://arxiv.org/abs/2408.12373v2
- Zhuo Zheng, Yanfei Zhong, Liangpei Zhang, Stefano Ermon. (2024) Segment Any Change. arXiv. http://arxiv.org/abs/2402.01188v4

