# Brain tumour segmentation with incomplete imaging data
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6782948.svg)](https://doi.org/10.5281/zenodo.6782948)

This is a repository hosting **all models** detailed in the article [Brain tumour segmentation with incomplete imaging data](https://arxiv.org/abs/2206.06120).

![Overview](assets/graphical_abstract.jpg)

## What is this repository for?
Brain tumour segmentation is **difficult in real-world practice**. Clinical imaging is very **heterogenous**.

Most brain tumour segmentation models available require multimodal MRI with four structural sequences: FLAIR, T1-weighted, T2-weighted, and contrast-enhanced T1-weighted sequences (T1CE)

But this ‘perfect’ and complete data is **often rare in clinical practice** 

We provide a solution to this problem with a modelling framework able to utilise any possible combination of these four MRI sequences, for both brain tumour tissue class segmentation (enhancing tumour, non-enhancing tumour, and perilesional oedema), and general abnormality detection.

This work substantially extends the translational opportunity for quantitative analysis to clinical situations where the full complement of sequences is not available, and potentially enables the characterisation of contrast-enhanced regions where contrast administration is infeasible or undesirable.



## Anticipated performances for specific sequence combinations
Models trained on incomplete data can segment lesions very well, often equivalently to those trained on the full completement of images, exhibiting Dice coefficients of 0.907 (single sequence) to 0.945 (complete set) for whole tumours, and 0.701 (single sequence) to 0.891 (complete set) for component tissue types. This opens the door both to the application of segmentation models to large-scale historical data, for the purpose of building treatment and outcome predictive models, and their application to real-world clinical care. A heatmap of model performances across all sequence combinations and tissue classes is shown below.

![Overview](assets/figure1.jpg)
**Performance of all model combinations.** A) Heatmap illustrates the validation Dice coefficient across all models, for both whole tumour and the individual components. Models are partitioned into those which utilized just one sequence, two, three and finally the complete four- sequence model. A brighter orange/white box depicts a better performing model as per the Dice coefficient. B) Second heatmap depicts the relative acquisition time (TA) (in minutes) for the sequences used for a given model, with a more green/yellow box illustrating a longer acquisition time. C) Third heatmap illustrates the performance gain in Dice coefficient per minute of acquisition time. The mathematical derivation of the Dice coefficient is given in the methods. Colour keys are given at the right of the plot.

## Detecting enhancing tumour without contrast-enhanced imaging
Not all patients can receive intravenous contrast for post-contrast MRI sequence acquistion.
For example, patients allergic to contrast, those in renal failure who cannot receive it, or where contrast use should be minimised (regular follow-up).

We show that segmentation models can detect enhancing tumour in the absence of contrast-enhancing imaging, quantifying the burden of enhancing tumour with an R2 > 0.97, varying negligibly with lesion morphology.

![Overview](assets/figure2.jpg)
**Examples of segmenting enhancing tumour without contrast.** A-C) Left two columns and rows of each panel illustrate the anatomical imaging for three randomly selected cases, whilst the third column of each panel illustrates the hand-labelled ground truth shown with the overlayed T1CE image, and finally the model prediction where contrast imaging was not provided. Of note, the case in panel B comprised a tumour with only a 7mm diameter enhancing component. D) The volume of enhancing tumour is highly significantly correlated to that of all model predictions, even when contrast-enhanced imaging is not provided (quantified by linear regression).

## Usage instructions
**1. Install [nnU-Net v1](https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1)** *Use of a CUDA-enabled GPU is strongly recommended.*
**2. Download our model weights here: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6782948.svg)](https://doi.org/10.5281/zenodo.6782948)
**3. Skull-strip your data (if not already done): All models must be used with skull-stripped images.** If not already done, there are many ways to do this, though we personally recommend [HD-BET](https://github.com/MIC-DKFZ/HD-BET).
**4. For using a specific model / sequence combinbation, see section **
**5. Where MRI sequence availabilty differs across the cohort, see section which incoporates our autosegmentation tool**


## Usage for specific model / sequence combination
This closely follows the [instructions for model inference with nnU-Net](https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1#run-inference)
Where a specific set of sequences are available, you can run segmentation with the following:

[nnU-Net](https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1) expects multimodal data to be suffixed numerically as follows: patient_id_0000.nii.gz, patient_id_0001.nii.gz, patient_id_0002.nii.gz, patient_id_0003.nii.gz. Sequence data must be labelled as such in the order as depicted by the model name. For example, model **Task900_BrainTumour2021_FlairT1CE** expects two files only, a **FLAIR** image (patient_id_0000.nii.gz), and a **T1CE** image (patient_id_0001.nii.gz). Not following this numbering system, or labelling sequences out of order to the model name will cause problems.

```
nnUNet_predict -i INPUT_FOLDER -o OUTPUT_FOLDER -t TASK_NAME_OR_ID -f all
```
where ```-t TASK_NAME_OR_ID``` denotes a specific model to be used.
n.b. ```-f``` should always be kept as ```all```

### Example use case
If a patient has T1-weighted, T2-weighted, and FLAIR MRI sequences, *but lacks the post-contrast T1 (T1CE)*, and we wish to undertake *lesion tissue class segmentation*, we should use the model **Task904_BrainTumour2021_FlairT1T2**. To do this, a folder containing sequences in the following order: **FLAIR** patient_id_0000.nii.gz, **T1** patient_id_0001.nii.gz, **T2** patient_id_0002.nii.gz. For example purposes, we will consider the patient directory to be ```/home/jruffle/example_patient/```.

Having done this, you can simply pass:
```
nnUNet_predict -i /home/jruffle/example_patient/ -o /home/jruffle/example_patient/ -t Task904_BrainTumour2021_FlairT1T2 -f all
```


## Usage with variable sequence availability for patients
Often not all MRI sequences are available for all patients. Rather than discount either patients with incomplete data, or disregard sequences that aren't available for everyone, **we provide here a pipeline to automatically detect sequence availability for each given patient, then segment each patient's lesion with the appropriate model.**

### Requirements
1. [Python](https://www.python.org/downloads/release/python-3106/) - developed with v. 3.10.6 though will likely with many historical verisons.
2. [NumPy] (https://pypi.org/project/numpy/)
3. [Pandas] (https://pypi.org/project/pandas/)
4. [tqdm] (https://pypi.org/project/tqdm/)
5. [DateTime] (https://pypi.org/project/DateTime/)
6. [argparse] (https://pypi.org/project/argparse/)

### Example use case
We have a directory of patient studies, for example in ```/home/jruffle/patient_studies/```. There are 3 patients, each with their own directory, ```patient_0```, ```patient_1```, ```patient_2```, and so on. We also create a .txt file of the participants to be worked on, in this example ```subs.txt ```, which contains on newlines:
```
patient_0
patient_1
patient_2
```
Inside each patient directory are any number of NIFTI images, titled as FLAIR.nii.gz, T1.nii.gz, T2.nii.gz, T1CE.nii.gz, as appropriate. Some patients may have all 4 sequences, some only 1, and some any combination. 

We then use the python script ```detect_and_segment.py```, also specifying whether to undertake multiclass lesion tissue segmentation, or general abnormality detection. In this case, we may call:
```
python detect_and_segment.py --path /home/jruffle/patient_studies/ --subs subs.txt --mode tissue 
```
which will iterate through the patients, determine the MRI sequences available, and call upon the appropriate lesion segmentation model for the sequences identified. 

Further description of the options with argparse can be shown with ```python detect_and_segment.py -h```



## Citation
If using these works, please cite the following [paper](https://arxiv.org/abs/2206.06120)

James K Ruffle, Samia Mohinta, Robert Gray, Harpreet Hyare, Parashkev Nachev. Brain tumour segmentation with incomplete imaging data. Brain Communications. 2023. DOI 10.1093/braincomms/fcad118


## Usage queries
Via github issue log or email to j.ruffle@ucl.ac.uk



## Funders
The Wellcome Trust; UCLH NIHR Biomedical Research Centre; Medical Research Council; Guarantors of Brain; NHS Topol Digital Fellowship
