## Executive summary

Reviewed 10 papers across 1 venues. We summarize methods, results, and limitations, and identify common gaps.

## Comparative matrix

| Paper | Venue | Year | Citations | Methods | Results | Limitations |
| --- | --- | --- | --- | --- | --- | --- |
| GRIT: Graph-Regularized Logit Refinement for Zero-shot Cell Type
  Annotation | arXiv | 2025 |  |  |  |  |
| GenoHoption: Bridging Gene Network Graphs and Single-Cell Foundation
  Models | arXiv | 2024 |  |  |  |  |
| ChromFound: Towards A Universal Foundation Model for Single-Cell
  Chromatin Accessibility Data | arXiv | 2025 |  |  |  |  |
| Unlocking Practical Applications in Legal Domain: Evaluation of GPT for
  Zero-Shot Semantic Annotation of Legal Texts | arXiv | 2023 |  |  |  |  |
| One-shot and Partially-Supervised Cell Image Segmentation Using Small
  Visual Prompt | arXiv | 2023 |  |  |  |  |
| Exploiting generative self-supervised learning for the assessment of
  biological images with lack of annotations: a COVID-19 case-study | arXiv | 2021 |  |  |  |  |
| Few-Shot Microscopy Image Cell Segmentation | arXiv | 2020 |  |  |  |  |
| CellStyle: Improved Zero-Shot Cell Segmentation via Style Transfer | arXiv | 2025 |  |  |  |  |
| CellViT++: Energy-Efficient and Adaptive Cell Segmentation and
  Classification Using Foundation Models | arXiv | 2025 |  |  |  |  |
| Self-Attention Diffusion Models for Zero-Shot Biomedical Image
  Segmentation: Unlocking New Frontiers in Medical Imaging | arXiv | 2025 |  |  |  |  |


## Mini-reviews

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

### Unlocking Practical Applications in Legal Domain: Evaluation of GPT for
  Zero-Shot Semantic Annotation of Legal Texts

arXiv, 2023, Jaromir Savelka

**TL;DR**

We evaluated the capability of a state-of-the-art generative pre-trained
transformer (GPT) model to perform semantic annotation of short text snippets
(one to few sentences) coming from legal documents of various types.
Discussions of potential uses (e.g., document drafting, summ...

**Critique**

- overclaiming: Claims strong superiority; check against baselines in paper. (severity: medium)
- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> We evaluated the capability of a state-of-the-art generative pre-trained
transformer (GPT) model to perform semantic annotation of short text snippets
(one to few sentences) coming from legal document (abstract)

### One-shot and Partially-Supervised Cell Image Segmentation Using Small
  Visual Prompt

arXiv, 2023, Sota Kato; Kazuhiro Hotta

**TL;DR**

Semantic segmentation of microscopic cell images using deep learning is an
important technique, however, it requires a large number of images and ground
truth labels for training. To address the above problem, we consider an
efficient learning framework with as little data as pos...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Semantic segmentation of microscopic cell images using deep learning is an
important technique, however, it requires a large number of images and ground
truth labels for training. To address the above (abstract)

### Exploiting generative self-supervised learning for the assessment of
  biological images with lack of annotations: a COVID-19 case-study

arXiv, 2021, Alessio Mascolini; Dario Cardamone; Francesco Ponzio; Santa Di Cataldo; Elisa Ficarra

**TL;DR**

Computer-aided analysis of biological images typically requires extensive
training on large-scale annotated datasets, which is not viable in many
situations. In this paper we present GAN-DL, a Discriminator Learner based on
the StyleGAN2 architecture, which we employ for self-sup...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Computer-aided analysis of biological images typically requires extensive
training on large-scale annotated datasets, which is not viable in many
situations. In this paper we present GAN-DL, a Discrim (abstract)

### Few-Shot Microscopy Image Cell Segmentation

arXiv, 2020, Youssef Dawoud; Julia Hornauer; Gustavo Carneiro; Vasileios Belagiannis

**TL;DR**

Automatic cell segmentation in microscopy images works well with the support
of deep neural networks trained with full supervision. Collecting and
annotating images, though, is not a sustainable solution for every new
microscopy database and cell type. Instead, we assume that we ...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Automatic cell segmentation in microscopy images works well with the support
of deep neural networks trained with full supervision. Collecting and
annotating images, though, is not a sustainable solut (abstract)

### CellStyle: Improved Zero-Shot Cell Segmentation via Style Transfer

arXiv, 2025, Rüveyda Yilmaz; Zhu Chen; Yuli Wu; Johannes Stegmaier

**TL;DR**

Cell microscopy data are abundant; however, corresponding segmentation
annotations remain scarce. Moreover, variations in cell types, imaging devices,
and staining techniques introduce significant domain gaps between datasets. As
a result, even large, pretrained segmentation mode...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Cell microscopy data are abundant; however, corresponding segmentation
annotations remain scarce. Moreover, variations in cell types, imaging devices,
and staining techniques introduce significant dom (abstract)

### CellViT++: Energy-Efficient and Adaptive Cell Segmentation and
  Classification Using Foundation Models

arXiv, 2025, Fabian Hörst; Moritz Rempe; Helmut Becker; Lukas Heine; Julius Keyl; Jens Kleesiek

**TL;DR**

Digital Pathology is a cornerstone in the diagnosis and treatment of
diseases. A key task in this field is the identification and segmentation of
cells in hematoxylin and eosin-stained images. Existing methods for cell
segmentation often require extensive annotated datasets for t...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Digital Pathology is a cornerstone in the diagnosis and treatment of
diseases. A key task in this field is the identification and segmentation of
cells in hematoxylin and eosin-stained images (abstract)

### Self-Attention Diffusion Models for Zero-Shot Biomedical Image
  Segmentation: Unlocking New Frontiers in Medical Imaging

arXiv, 2025, Abderrachid Hamrani; Anuradha Godavarty

**TL;DR**

Producing high-quality segmentation masks for medical images is a fundamental
challenge in biomedical image analysis. Recent research has explored
large-scale supervised training to enable segmentation across various medical
imaging modalities and unsupervised training to facilit...

**Critique**

- missing_baselines: Results do not clearly compare against established baselines. (severity: low)
- reproducibility: No mention of code/data availability or reproducibility. (severity: medium)

**Grounding quotes**

> Producing high-quality segmentation masks for medical images is a fundamental
challenge in biomedical image analysis. Recent research has explored
large-scale supervised training to enable segmentatio (abstract)

## Gaps & future work

- Few works report comparisons against strong baselines.
- Open-sourcing code and datasets
- Larger, diverse cohorts
- Robust baseline comparisons

### References

- Tianxiang Hu, Chenyi Zhou, Jiaxiang Liu, Jiongxin Wang, Ruizhe Chen, Haoxiang Xia, Gaoang Wang, Jian Wu, Zuozhu Liu. (2025) GRIT: Graph-Regularized Logit Refinement for Zero-shot Cell Type
  Annotation. arXiv. http://arxiv.org/abs/2508.04747v1
- Jiabei Cheng, Jiachen Li, Kaiyuan Yang, Hongbin Shen, Ye Yuan. (2024) GenoHoption: Bridging Gene Network Graphs and Single-Cell Foundation
  Models. arXiv. http://arxiv.org/abs/2411.06331v1
- Yifeng Jiao, Yuchen Liu, Yu Zhang, Xin Guo, Yushuai Wu, Chen Jiang, Jiyang Li, Hongwei Zhang, Limei Han, Xin Gao, Yuan Qi, Yuan Cheng. (2025) ChromFound: Towards A Universal Foundation Model for Single-Cell
  Chromatin Accessibility Data. arXiv. http://arxiv.org/abs/2505.12638v2
- Jaromir Savelka. (2023) Unlocking Practical Applications in Legal Domain: Evaluation of GPT for
  Zero-Shot Semantic Annotation of Legal Texts. arXiv. http://arxiv.org/abs/2305.04417v1
- Sota Kato, Kazuhiro Hotta. (2023) One-shot and Partially-Supervised Cell Image Segmentation Using Small
  Visual Prompt. arXiv. http://arxiv.org/abs/2304.07991v1
- Alessio Mascolini, Dario Cardamone, Francesco Ponzio, Santa Di Cataldo, Elisa Ficarra. (2021) Exploiting generative self-supervised learning for the assessment of
  biological images with lack of annotations: a COVID-19 case-study. arXiv. http://arxiv.org/abs/2107.07761v2
- Youssef Dawoud, Julia Hornauer, Gustavo Carneiro, Vasileios Belagiannis. (2020) Few-Shot Microscopy Image Cell Segmentation. arXiv. http://arxiv.org/abs/2007.01671v1
- Rüveyda Yilmaz, Zhu Chen, Yuli Wu, Johannes Stegmaier. (2025) CellStyle: Improved Zero-Shot Cell Segmentation via Style Transfer. arXiv. http://arxiv.org/abs/2503.08603v1
- Fabian Hörst, Moritz Rempe, Helmut Becker, Lukas Heine, Julius Keyl, Jens Kleesiek. (2025) CellViT++: Energy-Efficient and Adaptive Cell Segmentation and
  Classification Using Foundation Models. arXiv. http://arxiv.org/abs/2501.05269v1
- Abderrachid Hamrani, Anuradha Godavarty. (2025) Self-Attention Diffusion Models for Zero-Shot Biomedical Image
  Segmentation: Unlocking New Frontiers in Medical Imaging. arXiv. http://arxiv.org/abs/2503.18170v1

