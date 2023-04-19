#	autosegment.py | a pipeline for automated brain tumour segmentation with variable MRI sequence availability
#
#	Citation | James K Ruffle, Samia Mohinta, Robert Gray, Harpreet Hyare, Parashkev Nachev. Brain tumour segmentation with incomplete imaging data. Brain Communications. 2023. 
#	DOI 10.1093/braincomms/fcad118
#
#	Copyright 2023 James Ruffle, High-Dimensional Neurology, UCL Queen Square Institute of Neurology.
#
#	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
#	as published the Free Software Foundation, either version 3 of the License, or any later.
#
#	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
#
#	See the GNU General Public License for more details.
#	You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#	This code is part of the repository https://github.com/high-dimensional/tumour-seg
#
#	Correspondence to Dr James K Ruffle by email: j.ruffle@ucl.ac.uk

import glob
import numpy as np
import sys
import os 
import pandas as pd
import shutil
import errno
import subprocess
from datetime import datetime
import argparse
from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument("--path", type=str, default='/home/jruffle/patient_studies/', help='path of subject data, default=/home/jruffle/patient_studies/')
parser.add_argument("--subs", type=str, default='subs.txt', help='subject textfile for script to iterate through, default=subs.txt')
parser.add_argument("--mode", type=str, default='tissue', help='Whether to perform multiclass lesion tissue segmentation, or general abnormality detection, option is either "tissue" or "abnormality", default=tissue')
parser.add_argument("--nocleanup", action='store_true', help='whether to prevent clean-up of temporary files, disabled by default')
args = parser.parse_args()

sequences = ['FLAIR','T1','T1CE','T2']
inpath = args.path
subs = np.loadtxt(inpath+args.subs,dtype=str)
print("Number of unique patients: "+str(len(subs)))

Task890_BrainTumour2021_Flair = sorted(['FLAIR'])
Task891_BrainTumour2021_T1 = sorted(['T1'])
Task892_BrainTumour2021_T2 = sorted(['T2'])
Task893_BrainTumour2021_T1CE = sorted(['T1CE'])

Task894_BrainTumour2021_FlairAbnormality = sorted(['FLAIR'])
Task895_BrainTumour2021_T1Abnormality = sorted(['T1'])
Task896_BrainTumour2021_T2Abnormality = sorted(['T2'])
Task897_BrainTumour2021_T1CEAbnormality = sorted(['T1CE'])

Task898_BrainTumour2021_FlairT1 = sorted(['FLAIR', 'T1'])
Task899_BrainTumour2021_FlairT2 = sorted(['FLAIR', 'T2'])
Task900_BrainTumour2021_FlairT1CE = sorted(['FLAIR', 'T1CE'])
Task901_BrainTumour2021_T1T2 = sorted(['T1', 'T2'])
Task902_BrainTumour2021_T1T1CE = sorted(['T1', 'T1CE'])
Task903_BrainTumour2021_T2T1CE = sorted(['T2', 'T1CE'])

Task904_BrainTumour2021_FlairT1T2 = sorted(['FLAIR', 'T1', 'T2'])
Task905_BrainTumour2021_FlairT1T1CE = sorted(['FLAIR', 'T1', 'T1CE'])
Task906_BrainTumour2021_FlairT2T1CE = sorted(['FLAIR', 'T2', 'T1CE'])
Task907_BrainTumour2021_T1T2T1CE = sorted(['T1', 'T2', 'T1CE'])

Task908_BrainTumour2021_FlairT1Abnormality = sorted(['FLAIR', 'T1'])
Task909_BrainTumour2021_FlairT2Abnormality = sorted(['FLAIR', 'T2'])
Task910_BrainTumour2021_FlairT1CEAbnormality = sorted(['FLAIR', 'T1CE'])
Task911_BrainTumour2021_T1T2Abnormality = sorted(['T1', 'T2'])
Task912_BrainTumour2021_T1T1CEAbnormality = sorted(['T1', 'T1CE'])
Task913_BrainTumour2021_T2T1CEAbnormality = sorted(['T2', 'T1CE'])

Task914_BrainTumour2021_FlairT1T2Abnormality= sorted(['FLAIR', 'T1', 'T2'])
Task915_BrainTumour2021_FlairT1T1CEAbnormality = sorted(['FLAIR', 'T1', 'T1CE'])
Task916_BrainTumour2021_FlairT2T1CEAbnormality = sorted(['FLAIR', 'T2', 'T1CE'])
Task917_BrainTumour2021_T1T2T1CEAbnormality = sorted(['T1', 'T2', 'T1CE'])

Task918_BrainTumour2021_allseq_bratsonly = sorted(['FLAIR', 'T1', 'T2', 'T1CE'])
Task919_BrainTumour2021_allseq_bratsonly_abnormality = sorted(['FLAIR', 'T1', 'T2', 'T1CE'])

for i in tqdm(range(len(subs))):
    patient_id = subs[i]
    start = datetime.now()
    print("")
    print("Patient "+str(i+1)+'/'+str(len(subs)))
    print("Patient ID: "+str(patient_id))
    print("")
         
    temporary_working_dir = inpath+str(patient_id)+'/'

    try:
        shutil.rmtree(temporary_working_dir+'segmentation')
    except OSError as exc:
        pass

    try:
        os.mkdir(temporary_working_dir+'segmentation')
    except OSError as exc:
        pass

    try:
        shutil.rmtree(temporary_working_dir+'segmentation/tmpdir')
    except OSError as exc:
        pass

    try:
        os.mkdir(temporary_working_dir+'segmentation/tmpdir')
    except OSError as exc:
        pass

    superres = sorted(glob.glob(temporary_working_dir+'*gz'))
    superres = [i for i in superres if not ('mask' in i)]

    if len(superres) > 0:
        superres_df = pd.DataFrame(superres)
        superres_df=superres_df[0].str.split('/', expand=True)

        sequences_available = sorted(list(superres_df.iloc[:,-1].values))
        sequences_available = [w.replace('.nii.gz', '') for w in sequences_available]
        sequences_available = [w.replace('image_', '') for w in sequences_available]
        print("")
        print('Imaging available: '+str(sequences_available))

        ###one sequence models
        if sequences_available == Task890_BrainTumour2021_Flair and sequences_available == Task894_BrainTumour2021_FlairAbnormality:
            tissue_class_model = 'Task890_BrainTumour2021_Flair'
            abnormality_model = 'Task894_BrainTumour2021_FlairAbnormality'
            revised_filenames = dict({'FLAIR.nii.gz':'image_0000.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task891_BrainTumour2021_T1 and sequences_available == Task895_BrainTumour2021_T1Abnormality:
            tissue_class_model = 'Task891_BrainTumour2021_T1'
            abnormality_model = 'Task895_BrainTumour2021_T1Abnormality'
            revised_filenames = dict({'T1.nii.gz':'image_0000.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task893_BrainTumour2021_T1CE and sequences_available == Task897_BrainTumour2021_T1CEAbnormality:
            tissue_class_model = 'Task893_BrainTumour2021_T1CE'
            abnormality_model = 'Task897_BrainTumour2021_T1CEAbnormality'
            revised_filenames = dict({'T1CE.nii.gz':'image_0000.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task892_BrainTumour2021_T2 and sequences_available == Task896_BrainTumour2021_T2Abnormality:
            tissue_class_model = 'Task892_BrainTumour2021_T2'
            abnormality_model = 'Task896_BrainTumour2021_T2Abnormality'
            revised_filenames = dict({'T2.nii.gz':'image_0000.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))


        ###two sequence models
        if sequences_available == Task898_BrainTumour2021_FlairT1 and sequences_available == Task908_BrainTumour2021_FlairT1Abnormality:
            tissue_class_model = 'Task898_BrainTumour2021_FlairT1'
            abnormality_model = 'Task908_BrainTumour2021_FlairT1Abnormality'
            revised_filenames = dict({'FLAIR.nii.gz':'image_0000.nii.gz',
                                     'T1.nii.gz':'image_0001.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task899_BrainTumour2021_FlairT2 and sequences_available == Task909_BrainTumour2021_FlairT2Abnormality:
            tissue_class_model = 'Task899_BrainTumour2021_FlairT2'
            abnormality_model = 'Task909_BrainTumour2021_FlairT2Abnormality'
            revised_filenames = dict({'FLAIR.nii.gz':'image_0000.nii.gz',
                                     'T2.nii.gz':'image_0001.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task900_BrainTumour2021_FlairT1CE and sequences_available == Task910_BrainTumour2021_FlairT1CEAbnormality:
            tissue_class_model = 'Task900_BrainTumour2021_FlairT1CE'
            abnormality_model = 'Task910_BrainTumour2021_FlairT1CEAbnormality'
            revised_filenames = dict({'FLAIR.nii.gz':'image_0000.nii.gz',
                                     'T1CE.nii.gz':'image_0001.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task901_BrainTumour2021_T1T2 and sequences_available == Task911_BrainTumour2021_T1T2Abnormality:
            tissue_class_model = 'Task901_BrainTumour2021_T1T2'
            abnormality_model = 'Task911_BrainTumour2021_T1T2Abnormality'
            revised_filenames = dict({'T1.nii.gz':'image_0000.nii.gz',
                                     'T2.nii.gz':'image_0001.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task902_BrainTumour2021_T1T1CE and sequences_available == Task912_BrainTumour2021_T1T1CEAbnormality:
            tissue_class_model = 'Task902_BrainTumour2021_T1T1CE'
            abnormality_model = 'Task912_BrainTumour2021_T1T1CEAbnormality'
            revised_filenames = dict({'T1.nii.gz':'image_0000.nii.gz',
                                     'T1CE.nii.gz':'image_0001.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task903_BrainTumour2021_T2T1CE and sequences_available == Task913_BrainTumour2021_T2T1CEAbnormality:
            tissue_class_model = 'Task903_BrainTumour2021_T2T1CE'
            abnormality_model = 'Task913_BrainTumour2021_T2T1CEAbnormality'
            revised_filenames = dict({'T1CE.nii.gz':'image_0000.nii.gz',
                                     'T2.nii.gz':'image_0001.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))


        ###three sequence models
        if sequences_available == Task904_BrainTumour2021_FlairT1T2 and sequences_available == Task914_BrainTumour2021_FlairT1T2Abnormality:
            tissue_class_model = 'Task904_BrainTumour2021_FlairT1T2'
            abnormality_model = 'Task914_BrainTumour2021_FlairT1T2Abnormality'
            revised_filenames = dict({'FLAIR.nii.gz':'image_0000.nii.gz',
                                     'T1.nii.gz':'image_0001.nii.gz',
                                     'T2.nii.gz':'image_0002.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task905_BrainTumour2021_FlairT1T1CE and sequences_available == Task915_BrainTumour2021_FlairT1T1CEAbnormality:
            tissue_class_model = 'Task905_BrainTumour2021_FlairT1T1CE'
            abnormality_model = 'Task915_BrainTumour2021_FlairT1T1CEAbnormality'
            revised_filenames = dict({'FLAIR.nii.gz':'image_0000.nii.gz',
                                     'T1.nii.gz':'image_0001.nii.gz',
                                     'T1CE.nii.gz':'image_0002.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task906_BrainTumour2021_FlairT2T1CE and sequences_available == Task916_BrainTumour2021_FlairT2T1CEAbnormality:
            tissue_class_model = 'Task906_BrainTumour2021_FlairT2T1CE'
            abnormality_model = 'Task916_BrainTumour2021_FlairT2T1CEAbnormality'
            revised_filenames = dict({'FLAIR.nii.gz':'image_0000.nii.gz',
                                     'T1CE.nii.gz':'image_0001.nii.gz',
                                     'T2.nii.gz':'image_0002.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))

        if sequences_available == Task907_BrainTumour2021_T1T2T1CE and sequences_available == Task917_BrainTumour2021_T1T2T1CEAbnormality:
            tissue_class_model = 'Task907_BrainTumour2021_T1T2T1CE'
            abnormality_model = 'Task917_BrainTumour2021_T1T2T1CEAbnormality'
            revised_filenames = dict({'T1.nii.gz':'image_0000.nii.gz',
                                     'T1CE.nii.gz':'image_0001.nii.gz',
                                     'T2.nii.gz':'image_0002.nii.gz'})
            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))


        ###four sequence models
        if sequences_available == Task918_BrainTumour2021_allseq_bratsonly and sequences_available == Task919_BrainTumour2021_allseq_bratsonly_abnormality:
            tissue_class_model = 'Task918_BrainTumour2021_allseq_bratsonly'
            abnormality_model = 'Task919_BrainTumour2021_allseq_bratsonly_abnormality'
            revised_filenames = dict({'FLAIR.nii.gz':'image_0000.nii.gz',
                                     'T1.nii.gz':'image_0001.nii.gz',
                                     'T1CE.nii.gz':'image_0002.nii.gz',
                                     'T2.nii.gz':'image_0003.nii.gz'})

            print("Found candidate models: "+str(tissue_class_model)+', '+str(abnormality_model))


        for i, row in superres_df.iterrows():
            raw_fname = '/'.join(row[:len(row)])
            seq = superres_df.iloc[i,-1]
            revised_label_path = '/'.join(row[:len(row)-2])+'/'+patient_id+'/segmentation/tmpdir/'+str(revised_filenames[seq])
            shutil.copy(raw_fname,revised_label_path)

        INPUT_FOLDER = '/'.join(row[:len(row)-2])+'/'+patient_id+'/'+'segmentation/tmpdir/'
        OUTPUT_FOLDER = '/'.join(row[:len(row)-2])+'/'+patient_id+'/'+'/segmentation/'

        print("")
        if args.mode=='tissue':
            print("Running tissue class inference...")
            bashCommand = 'nnUNet_predict -i '+str(INPUT_FOLDER)+' -o '+str(OUTPUT_FOLDER)+' -t '+str(tissue_class_model)+' -f all'
            print(bashCommand)
            subprocess.run(bashCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            print("Inference complete!")


        if args.mode=='abnormality':
            print("Running general abnormality inference...")
            bashCommand = 'nnUNet_predict -i '+str(INPUT_FOLDER)+' -o '+str(OUTPUT_FOLDER)+' -t '+str(abnormality_model)+' -f all'
            print(bashCommand)
            subprocess.run(bashCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            print("Inference complete!")

    else:
        print('**Warning** No usable imaging found, moving to next accession')

    if not args.nocleanup:
        print("")
        print("Cleaning up")
        print("")
        try:
            shutil.rmtree(INPUT_FOLDER)
        except OSError as exc:
            pass
    
    end = datetime.now()
    difference = end - start
    seconds_in_day = 24 * 60 * 60
    difference = divmod(difference.days * seconds_in_day + difference.seconds, 60)
    time_taken= difference[0]+(difference[1]/60)
    print("Time taken on this patient_id: "+str(np.round(time_taken,2))+' mins')
    print("")

