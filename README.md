# Brain tumour segmentation with incomplete imaging data

This is a repository hosting all models detailed in the article [Brain tumour segmentation with incomplete imaging data](https://doi.org/10.1093/braincomms/fcad118).


The accompanying model weights for this repository can be downloaded here at:  [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7840171.svg)](https://doi.org/10.5281/zenodo.7840171)



![Overview](assets/graphical_abstract.jpg)


## Table of Contents
- [What is this repository for?](#what-is-this-repository-for)
  - [Typical performances for specific MRI sequence combinations](#typical-performances-for-specific-mri-sequence-combinations)
  - [Detecting enhancing tumour without contrast-enhanced imaging](#detecting-enhancing-tumour-without-contrast-enhanced-imaging)
- [Usage instructions](#usage-instructions)
  -  [Using a specific model / sequence combination](#using-a-specific-model--sequence-combination)
  -  [With variable sequence availability across your cohort](#with-variable-sequence-availability-across-your-cohort)
- [Efficiency](#efficiency)
- [Usage queries](#usage-queries)
- [Citation](#citation)
- [Funding](#funding)


## What is this repository for?
Brain tumour segmentation is **difficult in real-world clinical practice**. Clinical imaging is often **heterogenous**.

Most brain tumour segmentation models available require multimodal MRI with four structural sequences: FLAIR, T1-weighted, T2-weighted, and contrast-enhanced T1-weighted sequences (T1CE).

But, this ‘perfect’ and complete imaging data is comparatively **rare in clinical practice**.

**We provide a solution to this problem** with a modelling framework able to utilise *any possible combination of these four MRI sequences*, for both brain tumour lesion tissue class segmentation (enhancing tumour, non-enhancing tumour, and perilesional oedema), and general abnormality detection.

This work substantially extends the **translational opportunity for quantitative imaging analysis to clinical situations where the full complement of sequences is not available, and potentially enables the characterisation of contrast-enhanced regions where contrast administration is infeasible or undesirable.**


## Typical performances for specific MRI sequence combinations
Models trained on incomplete data can segment lesions very well, **often equivalently to those trained on the full completement of images**, exhibiting Dice coefficients of 0.907 (single sequence) to 0.945 (complete set) for whole tumours, and 0.701 (single sequence) to 0.891 (complete set) for component tissue types. This **opens the door both to the application of segmentation models to large-scale historical data, for the purpose of building treatment and outcome predictive models, and their application to real-world clinical care.** A heatmap of model performances across all sequence combinations and tissue classes is shown below.

![Overview](assets/figure1.jpg)
**Performance of all model combinations.** A) Heatmap illustrates the validation Dice coefficient across all models, for both whole tumour and the individual tissue components. Models are partitioned into those which utilized just one sequence, two, three and finally the complete four- sequence model. A brighter orange/white box depicts a better performing model as per the Dice coefficient. B) Second heatmap depicts the relative acquisition time (TA) in minutes for the sequences used for a given model, with a more green/yellow box illustrating a longer acquisition time *(based on MRI sequence acquisition time at our centre as of April 2023)*. C) Third heatmap illustrates the performance gain in Dice coefficient per minute of acquisition time. Colour keys are given at the right of the plot.


## Detecting enhancing tumour without contrast-enhanced imaging
**Not all patients can receive intravenous contrast for post-contrast MRI sequence acquistion.**
For example, patients allergic to contrast, those in renal failure where it is contraindicated. There are numerous further use cases where minimizing contrast use is desirable, such as with regular follow-up.

**We show that segmentation models can detect enhancing tumour in the absence of contrast-enhancing imaging,** quantifying the burden of enhancing tumour with an R2 > 0.97, varying negligibly with lesion morphology.

![Overview](assets/figure2.jpg)
**Examples of segmenting enhancing tumour without contrast.** A-C) Left two columns and rows of each panel illustrate the anatomical imaging for three randomly selected cases, whilst the third column of each panel illustrates the hand-labelled ground truth shown with the overlayed T1CE image, and finally the *model prediction where contrast imaging was not provided*. Of note, the case in panel B comprised a tumour with only a 7mm diameter enhancing component. D) The volume of enhancing tumour is significantly correlated across all model predictions, even when contrast-enhanced imaging is not provided.


## Usage instructions
1. Install [nnU-Net v1](https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1) | *N.B. use of a CUDA-supported GPU is strongly recommended.*
2. Download our model weights [here](https://doi.org/10.5281/zenodo.7840171).
3. Skull-strip your data. *All models have been trained to expect skull-stripped images. If not already done, there are many ways to do this, though we personally recommend [HD-BET](https://github.com/MIC-DKFZ/HD-BET).*
4. For using a specific model / sequence combinbation, see [here](#Using-a-specific-model--sequence-combination).
5. Where MRI sequence availabilty differs across the cohort, see [here](#with-variable-sequence-availability-across-your-cohort).

  
### Using a specific model / sequence combination
This closely follows the [instructions for model inference with nnU-Net](https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1#run-inference)
Where a specific set of sequences are available, you can run segmentation with the following:

[nnU-Net](https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1) expects multimodal data to be suffixed numerically as follows: ```patient_id_0000.nii.gz```, ```patient_id_0001.nii.gz```, ```patient_id_0002.nii.gz```, ```patient_id_0003.nii.gz```. Sequence data must be labelled as such in the order as depicted by the model name.

For example, model ```Task900_BrainTumour2021_FlairT1CE``` expects **two files only**, a **FLAIR** image (```patient_id_0000.nii.gz```), and a **T1CE** image (```patient_id_0001.nii.gz```), **in that order**. Not following this numbering system, or labelling sequences out of order to the model name will cause problems. 

N.B. If using the fully multimodal (4 MRI sequence) model [i.e. either ```Task918_BrainTumour2021_allseq_bratsonly``` for multiclass lesion tissue segmentation, or ```Task919_BrainTumour2021_allseq_bratsonly_abnormality``` for general abnormality detection], then sequence labelling order **must follow the current [BraTS](http://braintumorsegmentation.org) convention**, which is as follows:

```
{'FLAIR.nii.gz':'image_0000.nii.gz',
'T1.nii.gz':'image_0001.nii.gz',
'T1CE.nii.gz':'image_0002.nii.gz',
'T2.nii.gz':'image_0003.nii.gz'}
```

The basic syntax to call a segmentation model is as follows:
```
nnUNet_predict -i INPUT_FOLDER -o OUTPUT_FOLDER -t TASK_NAME_OR_ID -f all
```
where ```-t TASK_NAME_OR_ID``` denotes a specific model to be used.
```-f``` should always be kept as ```all```.

#### Example use case
If a patient has T1-weighted, T2-weighted, and FLAIR MRI sequences, **but lacks the post-contrast T1 (T1CE)**, and we wish to undertake *lesion tissue class segmentation*, we should use the model ```Task904_BrainTumour2021_FlairT1T2```, with a directory containing sequences in the following order: **FLAIR** ```patient_id_0000.nii.gz```, **T1** ```patient_id_0001.nii.gz```, **T2** ```patient_id_0002.nii.gz```. For example purposes, we will consider the patient directory to be ```/home/jruffle/example_patient/```.

Having done this, you can simply pass:
```
nnUNet_predict -i /home/jruffle/example_patient/ -o /home/jruffle/example_patient/ -t Task904_BrainTumour2021_FlairT1T2 -f all
```


### With variable sequence availability across your cohort
Often, not all MRI sequences are available for all patients. Rather than discount either patients with incomplete data, or disregard sequences that aren't available for everyone, **we provide here a pipeline to automatically detect sequence availability for each patient, then segment each patient's tumour calling upon the appropriate model.**

#### Requirements
1. [Python](https://www.python.org/downloads/release/python-3106/)
2. [NumPy](https://pypi.org/project/numpy/)
3. [Pandas](https://pypi.org/project/pandas/)
4. [tqdm](https://pypi.org/project/tqdm/)
5. [DateTime](https://pypi.org/project/DateTime/)
6. [argparse](https://pypi.org/project/argparse/)

#### Example use case
We have a directory of patient studies, for example in ```/home/jruffle/patient_studies/```. There are 3 patients, each with their own directory, ```patient_0```, ```patient_1```, ```patient_2```. We also create a ```.txt``` file of the participants to be worked on, in this example named ```subs.txt ```, which contains patient IDs on newlines, as follows:
```
patient_0
patient_1
patient_2
```
Inside each patient directory are any number of NIFTIs, but those expected by the models need to be named as any of ```FLAIR.nii.gz```, ```T1.nii.gz```, ```T2.nii.gz```, ```T1CE.nii.gz```. Some patients may have all 4 sequences, some might have only 1, and others any other combination of the possible four. Those with no applicable imaging are ignored by the pipeline. **Our pipeline ```autosegment.py``` will recognise this data variability and select the most appropriate segmentation model for each individual patient.** 

In our example case, the directories contain the following:
```
/home/jruffle/patient_studies/
├──patient_0/
      ├──FLAIR.nii.gz
      ├──T1.nii.gz
      ├──T2.nii.gz
      ├──T1CE.nii.gz
├──patient_1/
      ├──FLAIR.nii.gz
├──patient_2/
      ├──T2.nii.gz
      ├──T1CE.nii.gz
```

We then use the python script ```autosegment.py```, also specifying whether to undertake *multiclass lesion tissue segmentation*, or *general abnormality detection*. In this example, we may call:
```
python autosegment.py --path /home/jruffle/patient_studies/ --subs subs.txt --mode tissue 
```
This will iterate through the patient list, determine the MRI sequences available **for each individual patient, and call the appropriate segmentation model for each individual** to conduct multiclass lesion tissue segmentation.

Further description of the options can be shown with ```python autosegment.py -h```


## Efficiency
On GPU-accelerated hardware (prototyped on a NVIDIA GeForce RTX 3090 Ti), time to segment per patient is approximately **10-15 seconds**.


## Usage queries
Via github issue log or email to j.ruffle@ucl.ac.uk


## Citation
If using these works, please cite the following [paper](https://doi.org/10.1093/braincomms/fcad118):

James K Ruffle, Samia Mohinta, Robert Gray, Harpreet Hyare, Parashkev Nachev. Brain tumour segmentation with incomplete imaging data. Brain Communications. 2023, Volume 5, Issue 2. DOI 10.1093/braincomms/fcad118


## Funding
The Wellcome Trust; UCLH NIHR Biomedical Research Centre; Medical Research Council; Guarantors of Brain; NHS Topol Digital Fellowship.
![funders](assets/funders.png)
