import os
import utils
import modelCaller

def analyse_part_license(input_folder: str, split_folder: str, output_folder: str, char_limit: int, system_prompt: str, user_prompt: str, model_name):
    # Step 1: Read all the paths of the txt files
    txt_files = utils.read_txt_files(input_folder)
    for file_path in txt_files:
        print(f"Processing file: {file_path}")

        # Step 2: Divide the text and save it
        split_files = utils.split_and_save_text(file_path, char_limit, split_folder)

        results = []
        base_name = os.path.basename(file_path).replace(".txt", "")

        # Step 3: Call the llm API to process the segmented text
        for i, split_file in enumerate(split_files, start=1):
            with open(split_file, "r", encoding="utf-8") as sf:
                text = sf.read()
            result = modelCaller.call_api(model_name, system_prompt, user_prompt, text)
            # Check if there is any contradiction in the attitude of the term.
            conflict_terms = utils.find_conflicting_terms(result)
            # Invoke the large model API to handle contradictions
            if conflict_terms:
                print(f"There is a term that has an attitude conflict: {str(conflict_terms)}")
                print("Call the repair agent")
                result_round_2 = modelCaller.call_api_round2(model_name, system_prompt, user_prompt, text, result, conflict_terms)
                result = utils.update_result_with_result_round_2(result, conflict_terms, result_round_2)
                print("Fixing completed by repair agent")
            results.append((i, result))

        # Step 4: Save the processing results
        utils.save_part_results(output_folder, base_name, results)

