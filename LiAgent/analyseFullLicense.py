import os
import utils
import modelCaller

def analyse_full_license(csv_file,input_folder: str, output_folder: str, system_prompt: str, user_prompt_1: str, user_prompt_2, terms_dict, model_name):
    """
        Only process the CSV files where multiple 'attitude' values are present, and pass the corresponding list of conflicting terms.
        """
    # Read the CSV file, identify the terms that have multiple "attitude" values, and return the corresponding file names along with the list of conflicting terms.
    conflicting_files = utils.get_conflicting_files(csv_file)
    for num, (file_name, conflict_terms) in enumerate(conflicting_files.items(), start=1):
        file_path = os.path.join(input_folder, file_name)
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping.")
            continue

        print(f"Processing file: {file_path}")
        print(f"conflict_terms: {conflict_terms}")

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Generate the section for term explanations
        selected_terms_definitions = "\n".join(
            [f"'{term}': '{terms_dict[term]}'" for term in conflict_terms]
        )

        user_prompt = user_prompt_1 + selected_terms_definitions + user_prompt_2
        result = modelCaller.call_api(model_name, system_prompt, user_prompt, text)

        # Check if there is any contradiction in the attitude of the term.
        conflict_terms = utils.find_conflicting_terms(result)
        # Fix
        if conflict_terms:
            print(f"There is a term that has an attitude conflict: {str(conflict_terms)}")
            print("Call the repair agent")
            result_round_2 = modelCaller.call_api_round2(model_name, system_prompt, user_prompt, text, result, conflict_terms)
            result = utils.update_result_with_result_round_2(result, conflict_terms, result_round_2)
            print("Fixing completed by repair agent")
        # Step 4: Save the processing results
        base_name = os.path.basename(file_path).replace(".txt", "")
        utils.save_global_results(output_folder, base_name, result)

