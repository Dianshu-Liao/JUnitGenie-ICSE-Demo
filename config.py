import os

class Config:


    current_dir = os.path.dirname(os.path.abspath(__file__))

    openai_key = 'your-key-here'
    LLM_CFGPath_ContextInfo_prompt_dir = current_dir + '/' + 'prompts/LLM_CFGPath_ContextInfo'
    LLM_CFGPath_prompt_dir = current_dir + '/' + 'prompts/LLM_CFGPath'
    LLM_Only_prompt_dir = current_dir + '/' + 'prompts/LLM_Only'
    LLM_CFGPath_SemanticContextInfo_prompt_dir = current_dir + '/' + 'prompts/LLM_CFGPath_SemanticContextInfo'
    LLM_ContextInfo_dir = current_dir + '/' + 'prompts/LLM_ContextInfo'
    Method_Constraints_prompt_dir = current_dir + '/' + 'prompts/Method_Constraints'
    CFG_Paths_Selector_prompt_dir = current_dir + '/' + 'prompts/CFG_Pruner'
    Parameters_Constraints_prompt_dir = current_dir + '/' + 'prompts/Parameters_Constraints'
    Code_Fixer_prompt_dir = current_dir + '/' + 'prompts/Code_Fixer'
    Check_Test_Oracle_dir = current_dir + '/' + 'prompts/Check_Test_Oracle'
    foundation_model_gpt4o = "gpt-4o"
    foundation_model_gpt4o_mini = "gpt-4o-mini"
    foundation_model_claude_3_5 = 'claude-3.5'
    path_selector_verification_time = 3


    # for the project org.apache.commons.lang3
    project_package_name = 'org.apache.commons.lang3'
    # testDir = "/Users/dianshuliao/Documents/Research/TestCaseGeneration/UnitTestGeneration/saved_data/experiment_results/Evosuite_and_Randoop/JavaProjects/commons-lang-master/src/test/java/org/apache/commons/lang3"

    # # current directory



    experiment_Result_Basic_Dir = current_dir + '/saved_data'
    ast_based_result_path = experiment_Result_Basic_Dir + '/' + 'Code_Knowledge_Base/' + project_package_name.replace('.', '_') + '/' + 'ASTBased_Results.csv'
    bytecode_based_result_path = experiment_Result_Basic_Dir + '/' + 'Code_Knowledge_Base/' + project_package_name.replace('.', '_') + '/' + 'ByteBased_Results.csv'


    entities_dir = experiment_Result_Basic_Dir + '/' + 'Code_Knowledge_Base/' + project_package_name.replace('.', '_') + '/' + 'Entities'
    relations_dir = experiment_Result_Basic_Dir + '/' + 'Code_Knowledge_Base/' + project_package_name.replace('.', '_') + '/' + 'Relations'


    cfg_path_construction_error_file_path = experiment_Result_Basic_Dir + '/' + 'Code_Knowledge_Base/' + project_package_name.replace('.', '_') + '/error_when_construct_cfg_paths.txt'



    field_entities_path = entities_dir + '/field_entities.csv'
    enum_constant_entities_path = entities_dir + '/enum_constant_entities.csv'
    method_entities_path = entities_dir + '/method_level_entities.csv'
    cfg_path_entities_path = entities_dir + '/cfg_path_entities.csv'
    uses_field_relations_path = relations_dir + '/uses_field.csv'
    uses_method_relations_path = relations_dir + '/uses_method.csv'
    uses_enum_constant_relations_path = relations_dir + '/uses_enum_constant.csv'
    has_cfg_path_relations_path = relations_dir + '/has_cfg_path.csv'

    class_path = current_dir + 'classpath.txt'
