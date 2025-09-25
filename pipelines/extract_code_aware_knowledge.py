import argparse
import sys
import os

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from pipelines.basic_entities_extraction import basic_entities_and_relations_extraction
from pipelines.obtain_cfg_paths import cfg_path_entities_and_relations_extraction
from pipelines.obtain_use_relevant_info_relations import uses_field_method_relations_construction
from config import Config
from utils import Util


def extract_code_aware_knowledge(package_name=None):
    # 如果提供了package_name，则动态更新Config中的package_name
    if package_name:
        print(f"Setting project package name to: {package_name}")
        Config.project_package_name = package_name
        # 重新计算依赖于package_name的路径
        _update_config_paths()
    
    print(f"Processing package: {Config.project_package_name}")
    print("Step 1: Extracting basic entities and relations...")
    basic_entities_and_relations_extraction()
    
    print("Step 2: Extracting CFG paths...")
    cfg_path_entities_and_relations_extraction()
    
    print("Step 3: Constructing usage relations...")
    uses_field_method_relations_construction()

    print("Step 4: Generating Neo4j import commands...")
    # cp the entities and relations to neo4j import directory
    command_statement = ''
    command_statement += 'sudo rm -rf /opt/homebrew/var/neo4j/data/databases/neo4j'
    command_statement += '\n'
    command_statement += 'sudo cp {}/*.csv /opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/'.format(
        Config.entities_dir)

    command_statement += '\n'
    command_statement += 'sudo cp {}/*.csv /opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/'.format(
        Config.relations_dir)

    command_statement += '\n'

    command_statement += '''neo4j-admin database import full \\
    --overwrite-destination=true \\
    --nodes=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/class_level_entities.csv \\
    --nodes=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/field_entities.csv \\
    --nodes=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/enum_constant_entities.csv \\
    --nodes=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/method_level_entities.csv \\
    --nodes=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/parameter_level_entities.csv \\
    --nodes=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/cfg_path_entities.csv \\
    --relationships=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/has_parameter_relations.csv \\
    --relationships=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/has_field_relations.csv \\
    --relationships=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/has_method_relations.csv \\
    --relationships=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/has_cfg_path.csv \\
    --relationships=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/has_enum_constant_relations.csv \\
    --relationships=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/uses_field.csv \\
    --relationships=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/uses_enum_constant.csv \\
    --relationships=/opt/homebrew/Cellar/neo4j/2025.01.0/libexec/import/uses_method.csv \\
    --verbose \\
    neo4j'''

    neo4j_import_command_file_path = Config.experiment_Result_Basic_Dir + '/'+ 'Code_Knowledge_Base/' + Config.project_package_name.replace('.',
                                                                                                                    '_') + '/neo4j_import_command.txt'
    
    # 确保目录存在
    os.makedirs(os.path.dirname(neo4j_import_command_file_path), exist_ok=True)
    Util.write_content_to_file(neo4j_import_command_file_path, command_statement)
    
    print(f"Neo4j import command saved to: {neo4j_import_command_file_path}")
    print("Code-aware knowledge extraction completed successfully!")


def _update_config_paths():
    """动态更新Config中依赖于project_package_name的路径"""
    Config.ast_based_result_path = Config.experiment_Result_Basic_Dir + '/' + 'Code_Knowledge_Base/' + Config.project_package_name.replace('.', '_') + '/' + 'ASTBased_Results.csv'
    Config.bytecode_based_result_path = Config.experiment_Result_Basic_Dir + '/' + 'Code_Knowledge_Base/' + Config.project_package_name.replace('.', '_') + '/' + 'ByteBased_Results.csv'
    
    Config.entities_dir = Config.experiment_Result_Basic_Dir + '/' + 'Code_Knowledge_Base/' + Config.project_package_name.replace('.', '_') + '/' + 'Entities'
    Config.relations_dir = Config.experiment_Result_Basic_Dir + '/' + 'Code_Knowledge_Base/' + Config.project_package_name.replace('.', '_') + '/' + 'Relations'
    
    Config.cfg_path_construction_error_file_path = Config.experiment_Result_Basic_Dir + '/' + 'Code_Knowledge_Base/' + Config.project_package_name.replace('.', '_') + '/error_when_construct_cfg_paths.txt'
    
    Config.field_entities_path = Config.entities_dir + '/field_entities.csv'
    Config.enum_constant_entities_path = Config.entities_dir + '/enum_constant_entities.csv'
    Config.method_entities_path = Config.entities_dir + '/method_level_entities.csv'
    Config.cfg_path_entities_path = Config.entities_dir + '/cfg_path_entities.csv'
    Config.uses_field_relations_path = Config.relations_dir + '/uses_field.csv'
    Config.uses_method_relations_path = Config.relations_dir + '/uses_method.csv'
    Config.uses_enum_constant_relations_path = Config.relations_dir + '/uses_enum_constant.csv'
    Config.has_cfg_path_relations_path = Config.relations_dir + '/has_cfg_path.csv'


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description='Extract code-aware knowledge from Java projects')
    parser.add_argument('--package', '-p', 
                       type=str, 
                       required=True,
                       help='Java package name to process (e.g., org.apache.commons.lang3)')
    
    args = parser.parse_args()
    
    package_name = args.package
    
    # 验证包名格式
    if not _is_valid_package_name(package_name):
        print(f"Warning: '{package_name}' might not be a valid Java package name.")
        print("Continuing with the provided package name...")
    
    try:
        extract_code_aware_knowledge(package_name)
    except Exception as e:
        print(f"Error during extraction: {e}")
        sys.exit(1)


def _is_valid_package_name(package_name):
    """简单验证Java包名格式"""
    import re
    # Java包名格式：由字母、数字、下划线和点组成，不能以数字开头
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$'
    return re.match(pattern, package_name) is not None

if __name__ == '__main__':
    main()
