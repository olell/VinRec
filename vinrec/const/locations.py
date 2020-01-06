DATA_DIR = "./vinrec_data"  # TODO: This might be done via config stuff

# Permanent directories
UNFINISHED_RECORDS = "{0}/records/unfinished".format(DATA_DIR)
FINISHED_RECORDS = "{0}/records/finished".format(DATA_DIR)

PERMANENT_DIRS = [
    UNFINISHED_RECORDS, FINISHED_RECORDS
]

# Temporary directories
TMP = "{0}/.vinrec_tmp".format(DATA_DIR)

TEMPORARY_DIRS = [
    TMP
]