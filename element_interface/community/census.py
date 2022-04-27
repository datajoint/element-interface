import os
import datajoint as dj

from . import parser

## mysql cluster
# dj.config['database.host'] = "mycluster.datajoint.io"
# dj.config['database.user'] = ""#os.getenv("DJ_USER", None)
# dj.config['database.password'] = ""#os.getenv("DJ_PASS", None)
# dj.config['database.port'] = 6446
# dj.config['database.use_tls'] = False

## tutorial-db
dj.config['database.host'] = "tutorial-db.datajoint.io"
dj.config['database.user'] = os.getenv("DJ_USER", None)
dj.config['database.password'] = os.getenv("DJ_PASS", None)

schema = dj.Schema("datajoint_community_census", locals())

@schema
class Public(dj.Manual):
    definition = """
    id: int auto_increment
    ---
    may_contact_raw = NULL : varchar(200)
    institution = NULL : varchar(20)
    department = NULL : varchar(20)
    lab = NULL : varchar(20)
    email = NULL : varchar(20)
    website = NULL : varchar(50)
    primary_discipline = NULL : varchar(20)
    major_focus = NULL : varchar(20)
    position = NULL : varchar(30)
    other_position = NULL : varchar(30)
    use_of_dj = NULL : varchar(300)
    year_using_dj = NULL : smallint unsigned
    how_using_dj = NULL : varchar(20)
    how_to_evolve = NULL : varchar(200)
    public_repo_raw = NULL : varchar(200)
    publications_raw = NULL : varchar(200)
    program_langs_raw = NULL : varchar(50)
    other_langs_raw = NULL : varchar(20)
    major_resouces_raw = NULL : varchar(150)
    other_resources_raw = NULL : varchar(50)
    exp_modalities_raw = NULL : varchar(850)
    other_modalities_raw = NULL : varchar(100)
    research_model_raw = NULL : varchar(300)
    other_model_raw = NULL : varchar(100)
    research_tools_raw = NULL : varchar(100)
    analysis_tools_raw = NULL : varchar(100)

    dj_user: varchar(50)
    report_time = CURRENT_TIMESTAMP : timestamp
    """

@schema
class PublicComputed(dj.Computed):
    definition = """
    -> Public
    ---
    agree_contact = 0 : tinyint(1)
    learn_more = 0 : tinyint(1)
    lang_python = 0 : tinyint(1)
    lang_matlab = 0 : tinyint(1)
    lang_other = 0 : tinyint(1)
    res_nwb = 0 : tinyint(1)
    res_dandi = 0 : tinyint(1)
    res_datalad = 0 : tinyint(1)
    res_bossdb = 0 : tinyint(1)
    res_openneuro = 0 : tinyint(1)
    res_ebrains = 0 : tinyint(1)
    res_other = 0 : tinyint(1)
    exp_colony = 0 : tinyint(1)
    exp_breeding = 0 : tinyint(1)
    exp_surgeries = 0 : tinyint(1)
    exp_behavioral_task = 0 : tinyint(1)
    exp_free_behavior = 0 : tinyint(1)
    exp_eeg = 0 : tinyint(1)
    exp_emg = 0 : tinyint(1)
    exp_neuroimaging = 0 : tinyint(1)
    exp_extracellular = 0 : tinyint(1)
    exp_intracellular = 0 : tinyint(1)
    exp_optical_imaging = 0 : tinyint(1)
    exp_calcium_imaging = 0 : tinyint(1)
    exp_voltage_imaging = 0 : tinyint(1)
    exp_optogenetic_stim = 0 : tinyint(1)
    exp_visual_stim = 0 : tinyint(1)
    exp_other_stim = 0 : tinyint(1)
    exp_electron_microscope = 0 : tinyint(1)
    exp_histology = 0 : tinyint(1)
    exp_singel_cell = 0 : tinyint(1)
    exp_other = 0 : tinyint(1)
    model_rodent = 0 : tinyint(1)
    model_nonhuman_primates = 0 : tinyint(1)
    model_human = 0 : tinyint(1)
    model_human_culture_organoids = 0 : tinyint(1)
    model_other_vertebrates = 0 : tinyint(1)
    model_invertebrates = 0 : tinyint(1)
    model_insilico_stim = 0 : tinyint(1)
    model_other = 0 : tinyint(1)

    ## maybe clean up multi-line input here
    # public_repo = NULL : varchar(200)
    # publications = NULL : varchar(200)
    # research_tools = NULL : varchar(100)
    # analysis_tools = NULL : varchar(100)
    """

    def make(self, key):
        """
        ## parse a row in the table
        ## - Square space checkbox selections are auto concatinated
        ## - Multi-line input areas
        """
        raw = (Public & key).fetch1()
        key.update(parser.parse_concat_checkbox_grp(raw))
        self.insert1(key)


@schema
class Private(dj.Manual):
    definition = """
    id: int auto_increment
    ---
    may_contact_raw = NULL : varchar(200)
    institution = NULL : varchar(20)
    department = NULL : varchar(20)
    lab = NULL : varchar(20)
    email = NULL : varchar(20)
    website = NULL : varchar(50)
    primary_discipline = NULL : varchar(20)
    major_focus = NULL : varchar(20)
    position = NULL : varchar(30)
    other_position = NULL : varchar(30)
    use_of_dj = NULL : varchar(300)
    year_using_dj = NULL : smallint unsigned
    how_using_dj = NULL : varchar(20)
    how_to_evolve = NULL : varchar(200)
    public_repo_raw = NULL : varchar(200)
    publications_raw = NULL : varchar(200)
    program_langs_raw = NULL : varchar(50)
    other_langs_raw = NULL : varchar(20)
    major_resouces_raw = NULL : varchar(150)
    other_resources_raw = NULL : varchar(50)
    exp_modalities_raw = NULL : varchar(850)
    other_modalities_raw = NULL : varchar(100)
    research_model_raw = NULL : varchar(300)
    other_model_raw = NULL : varchar(100)
    research_tools_raw = NULL : varchar(100)
    analysis_tools_raw = NULL : varchar(100)

    dj_user: varchar(50)
    report_time = CURRENT_TIMESTAMP : timestamp
    """

@schema
class PrivateComputed(dj.Computed):
    definition = """
    -> Private
    ---
    agree_contact = 0 : tinyint(1)
    learn_more = 0 : tinyint(1)
    lang_python = 0 : tinyint(1)
    lang_matlab = 0 : tinyint(1)
    lang_other = 0 : tinyint(1)
    res_nwb = 0 : tinyint(1)
    res_dandi = 0 : tinyint(1)
    res_datalad = 0 : tinyint(1)
    res_bossdb = 0 : tinyint(1)
    res_openneuro = 0 : tinyint(1)
    res_ebrains = 0 : tinyint(1)
    res_other = 0 : tinyint(1)
    exp_colony = 0 : tinyint(1)
    exp_breeding = 0 : tinyint(1)
    exp_surgeries = 0 : tinyint(1)
    exp_behavioral_task = 0 : tinyint(1)
    exp_free_behavior = 0 : tinyint(1)
    exp_eeg = 0 : tinyint(1)
    exp_emg = 0 : tinyint(1)
    exp_neuroimaging = 0 : tinyint(1)
    exp_extracellular = 0 : tinyint(1)
    exp_intracellular = 0 : tinyint(1)
    exp_optical_imaging = 0 : tinyint(1)
    exp_calcium_imaging = 0 : tinyint(1)
    exp_voltage_imaging = 0 : tinyint(1)
    exp_optogenetic_stim = 0 : tinyint(1)
    exp_visual_stim = 0 : tinyint(1)
    exp_other_stim = 0 : tinyint(1)
    exp_electron_microscope = 0 : tinyint(1)
    exp_histology = 0 : tinyint(1)
    exp_singel_cell = 0 : tinyint(1)
    exp_other = 0 : tinyint(1)
    model_rodent = 0 : tinyint(1)
    model_nonhuman_primates = 0 : tinyint(1)
    model_human = 0 : tinyint(1)
    model_human_culture_organoids = 0 : tinyint(1)
    model_other_vertebrates = 0 : tinyint(1)
    model_invertebrates = 0 : tinyint(1)
    model_insilico_stim = 0 : tinyint(1)
    model_other = 0 : tinyint(1)

    ## maybe clean up multi-line input here
    # public_repo = NULL : varchar(200)
    # publications = NULL : varchar(200)
    # research_tools = NULL : varchar(100)
    # analysis_tools = NULL : varchar(100)
    """

    def make(self, key):
        """
        ## parse a row in the table
        ## - Square space checkbox selections are auto concatinated
        ## - Multi-line input areas
        """
        raw = (Private & key).fetch1()
        key.update(parser.parse_concat_checkbox_grp(raw))
        self.insert1(key)

@schema
class Confidential(dj.Manual):
    definition = """
    id: int auto_increment
    ---
    may_contact_raw = NULL : varchar(200)
    institution = NULL : varchar(20)
    department = NULL : varchar(20)
    lab = NULL : varchar(20)
    email = NULL : varchar(20)
    website = NULL : varchar(50)
    primary_discipline = NULL : varchar(20)
    major_focus = NULL : varchar(20)
    position = NULL : varchar(30)
    other_position = NULL : varchar(30)
    use_of_dj = NULL : varchar(300)
    year_using_dj = NULL : smallint unsigned
    how_using_dj = NULL : varchar(20)
    how_to_evolve = NULL : varchar(200)
    public_repo_raw = NULL : varchar(200)
    publications_raw = NULL : varchar(200)
    program_langs_raw = NULL : varchar(50)
    other_langs_raw = NULL : varchar(20)
    major_resouces_raw = NULL : varchar(150)
    other_resources_raw = NULL : varchar(50)
    exp_modalities_raw = NULL : varchar(850)
    other_modalities_raw = NULL : varchar(100)
    research_model_raw = NULL : varchar(300)
    other_model_raw = NULL : varchar(100)
    research_tools_raw = NULL : varchar(100)
    analysis_tools_raw = NULL : varchar(100)

    dj_user: varchar(50)
    report_time = CURRENT_TIMESTAMP : timestamp
    """

@schema
class ConfidentialComputed(dj.Computed):
    definition = """
    -> Confidential
    ---
    agree_contact = 0 : tinyint(1)
    learn_more = 0 : tinyint(1)
    lang_python = 0 : tinyint(1)
    lang_matlab = 0 : tinyint(1)
    lang_other = 0 : tinyint(1)
    res_nwb = 0 : tinyint(1)
    res_dandi = 0 : tinyint(1)
    res_datalad = 0 : tinyint(1)
    res_bossdb = 0 : tinyint(1)
    res_openneuro = 0 : tinyint(1)
    res_ebrains = 0 : tinyint(1)
    res_other = 0 : tinyint(1)
    exp_colony = 0 : tinyint(1)
    exp_breeding = 0 : tinyint(1)
    exp_surgeries = 0 : tinyint(1)
    exp_behavioral_task = 0 : tinyint(1)
    exp_free_behavior = 0 : tinyint(1)
    exp_eeg = 0 : tinyint(1)
    exp_emg = 0 : tinyint(1)
    exp_neuroimaging = 0 : tinyint(1)
    exp_extracellular = 0 : tinyint(1)
    exp_intracellular = 0 : tinyint(1)
    exp_optical_imaging = 0 : tinyint(1)
    exp_calcium_imaging = 0 : tinyint(1)
    exp_voltage_imaging = 0 : tinyint(1)
    exp_optogenetic_stim = 0 : tinyint(1)
    exp_visual_stim = 0 : tinyint(1)
    exp_other_stim = 0 : tinyint(1)
    exp_electron_microscope = 0 : tinyint(1)
    exp_histology = 0 : tinyint(1)
    exp_singel_cell = 0 : tinyint(1)
    exp_other = 0 : tinyint(1)
    model_rodent = 0 : tinyint(1)
    model_nonhuman_primates = 0 : tinyint(1)
    model_human = 0 : tinyint(1)
    model_human_culture_organoids = 0 : tinyint(1)
    model_other_vertebrates = 0 : tinyint(1)
    model_invertebrates = 0 : tinyint(1)
    model_insilico_stim = 0 : tinyint(1)
    model_other = 0 : tinyint(1)

    ## maybe clean up multi-line input here
    # public_repo = NULL : varchar(200)
    # publications = NULL : varchar(200)
    # research_tools = NULL : varchar(100)
    # analysis_tools = NULL : varchar(100)
    """

    def make(self, key):
        """
        ## parse a row in the table
        ## - Square space checkbox selections are auto concatinated
        ## - Multi-line input areas
        """
        raw = (Confidential & key).fetch1()
        key.update(parser.parse_concat_checkbox_grp(raw))
        self.insert1(key)

raw_tables = [Public(), Private(), Confidential()]
computed_tables = [PublicComputed(), PrivateComputed(), ConfidentialComputed()]

def exec(cmd):
    if cmd == "show":
        for table in (raw_tables + computed_tables):
            print(table)
    if cmd == "compute":
        for table in computed_tables:
            table.populate()
    elif cmd == "drop raw":
        for table in raw_tables:
            table.drop()
    elif cmd == "drop computed":
        for table in computed_tables:
            table.drop()

if __name__ == "__main__":
    ## Make a .env file from .env.example
    # run this in cmd: `set -a && source .env`
    CMD = "show"
    exec(CMD)
