import analysePartLicense
import processPartData
import analyseFullLicense
import utils
import processFullData

if __name__ == "__main__":
    # Store the licenses that need to be processed
    INPUT_FOLDER = "license"
    SPLIT_FOLDER = "tmp/split_output"
    OUTPUT_FOLDER = "tmp/output"
    OUTPUT_FOLDER_2 = "tmp/output_2"
    part_attitude_file = "tmp/license_attitudes.csv"
    CHAR_LIMIT = 10000  # Maximum number of delimiter characters
    model_name = "deepseek-chat"

    with open("resources/prompts/systemPrompt.txt", "r", encoding="utf-8") as sf:
        system_prompt = sf.read()
    with open("resources/prompts/partUserPrompt.txt", "r", encoding="utf-8") as sf:
        user_prompt = sf.read()

    # Extract the segments after the license is segmented.
    analysePartLicense.analyse_part_license(INPUT_FOLDER, SPLIT_FOLDER, OUTPUT_FOLDER, CHAR_LIMIT, system_prompt, user_prompt, model_name)
    # process attitude
    processPartData.process_part_license_files(OUTPUT_FOLDER, part_attitude_file)

    terms_dict = utils.load_terms()
    with open("resources/prompts/globalUserPrompt1.txt", "r", encoding="utf-8") as sf:
        user_prompt_1 = sf.read()
    with open("resources/prompts/globalUserPrompt2.txt", "r", encoding="utf-8") as sf:
        user_prompt_2 = sf.read()
    # If there are conflicts after the summary of the local licenses, they need to be reprocessed.
    analyseFullLicense.analyse_full_license(part_attitude_file, INPUT_FOLDER, OUTPUT_FOLDER_2, system_prompt, user_prompt_1, user_prompt_2, terms_dict, model_name)

    result_csv_file = "result.csv"
    processFullData.process_full_license_files(part_attitude_file, result_csv_file, OUTPUT_FOLDER_2)

    utils.generate_license_summaries(result_csv_file)