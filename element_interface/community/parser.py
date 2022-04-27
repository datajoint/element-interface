def parse_concat_checkbox_grp(raw: dict) -> dict:
    CHECKBOX_GROUP_KEYS = (
        "may_contact_raw",
        "program_langs_raw",
        "research_model_raw",
        "exp_modalities_raw",
        "major_resouces_raw",
    )
    ATTR_LOOKUP = {
        "may_contact_raw_I agree to be contacted by the DataJoint team for further questions about my responses." : "agree_contact",
        "may_contact_raw_I am interested in learning more about managed services – DataJoint SciOps – to support my research.": "learn_more",
        "program_langs_raw_Python": "lang_python",
        "program_langs_raw_MATLAB": "lang_matlab",
        "program_langs_raw_Other(s)": "lang_other",
        "major_resouces_raw_Neurodata without Borders (NWB)": "res_nwb",
        "major_resouces_raw_DANDI Archive": "res_dandi",
        "major_resouces_raw_DataLad": "res_datalad",
        "major_resouces_raw_BossDB": "res_bossdb",
        "major_resouces_raw_OpenNeuro": "res_openneuro",
        "major_resouces_raw_EBRAINS": "res_ebrains",
        "major_resouces_raw_Other(s)": "res_other",
        "exp_modalities_raw_Colony management": "exp_colony",
        "exp_modalities_raw_Breeding / Genotyping": "exp_breeding",
        "exp_modalities_raw_Surgeries, procedures, water restriction, pharmacological interventions": "exp_surgeries",
        "exp_modalities_raw_Behavioral task trials (stimulus / response)": "exp_behavioral_task",
        "exp_modalities_raw_Free behavior tracking: pupil, locomotion, pose estimation": "exp_free_behavior",
        "exp_modalities_raw_EEG, ECoG": "exp_eeg",
        "exp_modalities_raw_EMG": "exp_emg",
        "exp_modalities_raw_Neuroimaging (e.g. fMRI, DTI)": "exp_neuroimaging",
        "exp_modalities_raw_Extracellular Electrophysiology (in vivo or slice)": "exp_extracellular",
        "exp_modalities_raw_Intracellular Electrophysiology (in vivo or slice)": "exp_intracellular",
        "exp_modalities_raw_Optical imaging of intrinsic signals": "exp_optical_imaging",
        "exp_modalities_raw_Calcium imaging of neuronal signals: widefield, multiphoton, miniscope, lightsheet, etc.": "exp_calcium_imaging",
        "exp_modalities_raw_Voltage imaging of neuronal signals: widefield, multiphoton, miniscope, lightsheet, etc.": "exp_voltage_imaging",
        "exp_modalities_raw_Optogenetic stimulation": "exp_optogenetic_stim",
        "exp_modalities_raw_Visual stimulation": "exp_visual_stim",
        "exp_modalities_raw_Other sensory stimulation: air puff, odor, audio": "exp_other_stim",
        "exp_modalities_raw_Electron Microscopy": "exp_electron_microscope",
        "exp_modalities_raw_Histology": "exp_histology",
        "exp_modalities_raw_Single-cell sequencing, transcriptomics": "exp_singel_cell",
        "exp_modalities_raw_Other": "exp_other",
        "research_model_raw_Rodent": "model_rodent",
        "research_model_raw_Non-human primates": "model_nonhuman_primates",
        "research_model_raw_Human": "model_human",
        "research_model_raw_Human patient-derived culture / organoids": "model_human_culture_organoids",
        "research_model_raw_Other vertebrates": "model_other_vertebrates",
        "research_model_raw_Invertebrates": "model_invertebrates",
        "research_model_raw_In-silico simulations and modeling": "model_insilico_stim",
        "research_model_raw_Other(s)": "model_other"
    }
    
    parsed_checkbox_grp = {
        k:[f"{k}_"+op.replace("> ", "").strip() for op in v.split(", > ")]
        for k,v in raw.items()
        if k in CHECKBOX_GROUP_KEYS and v
    }

    if parsed_checkbox_grp:
        return {ATTR_LOOKUP[_]:True for _ in sum(parsed_checkbox_grp.values(), [])}
    else:
        return { _:False for _ in ATTR_LOOKUP.values()}


