import shutil

BASES_TESTS_OUTPUT_DIR = "unit/utils/environment_utils/tests_output"

def clear_tests_ie_output():
    shutil.rmtree(f"{BASES_TESTS_OUTPUT_DIR}/personalai_env_ie_t3", ignore_errors=True)

def clear_tests_ss_output():
    shutil.rmtree(f"{BASES_TESTS_OUTPUT_DIR}/personalai_env_ss_t4", ignore_errors=True)
    shutil.rmtree(f"{BASES_TESTS_OUTPUT_DIR}/personalai_env_ss_t5", ignore_errors=True)
    shutil.rmtree(f"{BASES_TESTS_OUTPUT_DIR}/personalai_env_ss_t6", ignore_errors=True)