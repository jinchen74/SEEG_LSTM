# SEEG Project
## Introduction 

The focus point of this project is to research the difference between sleep of pre seizure and normal sleep.


## Data preprocessing 

You need read DataProcessing 

## How to run this project

MNE: pip install -U https://api.github.com/repos/mne-tools/mne-python/zipball/master

Python : pip install python 

You need run ./Seeg_VMAML_Double_Vae.py


## Content

**data**  There are some data about raw seeg data, processed data, and channels information.

**RelationNet**  including CNN coding, few-shot learning coding, and feature visualization methods.

**test** including testing methods.

**util**  including reading .*edf file methods, and filtering methods.

**MAML** including MAML model.

**VAML** A new model that combines vae and maml. --> the model was later renamed as PiSC 

**VAE** variational auto encode, coding seeg matrix.

**Visualization**  SEEG heatmap calculation

**Statistical files** Experimental result 

**Metalearning_Baselines** other meta learning models

pre_seizure: 1, normal_sleep:0







