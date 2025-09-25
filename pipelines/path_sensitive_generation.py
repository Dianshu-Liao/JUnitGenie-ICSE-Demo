import time
import subprocess
import argparse
import sys
import os
import re

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from pipelines.context_knowledge_distillation import construct_prompt_for_a_cfg_path
from config import Config
from llm_utils import LLM_Utils
from neo4jcommands import Neo4jCommands
from pipelines.code_formatting import get_runnable_code_from_test_code, empty_test_dir


def remove_inline_warnings(log_text):
    """
    从编译错误日志中移除警告信息，只保留错误信息
    """
    # 1. 先用正则删除整个以 warning: 开头的片段及其后一个 |
    cleaned = re.sub(r'warning:.*?(?=\|)', '', log_text)

    # 2. 再删掉可能在末尾的 warning 片段（如果没有 |）
    cleaned = re.sub(r'\|?\s*warning:.*$', '', cleaned)

    # 3. 清理多余的 |（多个连续 | 或 | 开头结尾）
    cleaned = re.sub(r'\s*\|\s*', ' | ', cleaned)  # 标准化间隔
    cleaned = re.sub(r'(\|\s*){2,}', '| ', cleaned)  # 连续多个 | 合并
    cleaned = re.sub(r'^\s*\|\s*', '', cleaned)  # 去掉开头的 |
    cleaned = re.sub(r'\s*\|\s*$', '', cleaned)  # 去掉结尾的 |

    return cleaned.strip()


def construct_code_refinement_prompt(error_message, test_code):
    """
    使用 Code_Fixer prompt 构建代码修复提示
    
    Args:
        error_message: 编译错误信息
        test_code: 需要修复的测试代码
    
    Returns:
        list: 格式化的提示消息列表
    """
    # 清理错误信息
    error_message = remove_inline_warnings(error_message).replace(' | ', '\n')
    
    # 读取系统提示
    system_prompt_path = Config.Code_Fixer_prompt_dir + '/System'
    system_prompt_content = LLM_Utils.read_prompt_file(system_prompt_path)
    system_prompt = [{'role': 'system', 'content': system_prompt_content}]
    
    # 读取输入提示模板
    input_prompt_path = Config.Code_Fixer_prompt_dir + '/Input'
    input_prompt_content = LLM_Utils.read_prompt_file(input_prompt_path)
    
    # 替换占位符
    input_prompt_content = input_prompt_content.replace('#{}#', test_code, 1)
    input_prompt_content = input_prompt_content.replace('#{}#', error_message, 1)
    
    input_prompt = [{'role': 'user', 'content': input_prompt_content}]
    code_refinement_prompt = system_prompt + input_prompt
    
    return code_refinement_prompt


def save_test_code_to_file(test_code, method_FEN, cfg_path_no, project_dir, package_name):
    # save test code to a file
    if '$' in method_FEN:
        class_name = method_FEN.split('$')[0].split('.')[-1]
    else:
        class_name = method_FEN.split('.')[-2]
    package_import_name = method_FEN.split('.' + class_name)[0]
    class_name = method_FEN.replace(package_name + '.', '').replace('.', '_').replace('(', '_').replace(')',
                                                                                                        '').replace(
        ',', '_').replace('[', '__').replace(']', '__').replace('$', '__dollarsign__').replace('<',
                                                                                               '_').replace(
        '>', '_') + '_cfg_path_' + str(cfg_path_no) + '_Test'
    test_code_after_formatting = get_runnable_code_from_test_code(test_code, package_import_name, class_name)
    saved_file_name = class_name + '.java'
    test_dir = project_dir + '/src/test/java/' + package_import_name.replace('.', '/')
    saved_path = f'{test_dir}/{saved_file_name}'

    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    f = open(saved_path, 'w')
    f.write(test_code_after_formatting)
    f.close()

    return saved_path, test_code_after_formatting


def compile_test_file(test_file_path, project_dir, classpath_file=None, max_retries=3):
    """
    编译Java测试文件并检查语法错误
    
    Args:
        test_file_path: 测试文件的完整路径
        project_dir: 项目目录
        classpath_file: classpath文件路径，如果为None则使用默认路径
        max_retries: 最大重试次数
    
    Returns:
        tuple: (success: bool, error_log: str, exit_code: int)
    """
    
    # 确保目标测试编译目录存在
    test_classes_dir = os.path.join(project_dir, 'target', 'test-classes')
    if not os.path.exists(test_classes_dir):
        os.makedirs(test_classes_dir)
    
    # 构建classpath
    if classpath_file and os.path.exists(classpath_file):
        classpath_cmd = f"$(cat {classpath_file})"
    else:
        # 尝试使用项目根目录下的classpath.txt
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        default_classpath_file = os.path.join(root_dir, 'classpath.txt')
        
        if os.path.exists(default_classpath_file):
            classpath_cmd = f"$(cat {default_classpath_file})"
        else:
            # 使用默认classpath
            classpath_cmd = "target/classes:src/main/java"
    
    # 将测试文件路径转为绝对路径
    abs_test_file_path = os.path.abspath(test_file_path)
    
    # 构建编译命令
    compile_cmd = (
        f"javac -cp {classpath_cmd} "
        f"-d target/test-classes "
        f"'{abs_test_file_path}'"
    )
    
    # print(f"Compiling: {os.path.basename(test_file_path)}")
    # print(f"Command: {compile_cmd}")
    
    try:
        # 执行编译命令
        result = subprocess.run(
            compile_cmd,
            shell=True,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30  # 30秒超时
        )
        
        success = result.returncode == 0
        error_log = result.stderr if result.stderr else result.stdout
        
        if success:
            print("✅ Test generation successful!")
        else:
            print(f"❌ Compilation failed with exit code: {result.returncode}")
            print(f"Error log: {error_log}")
        
        return success, error_log, result.returncode
        
    except subprocess.TimeoutExpired:
        error_msg = "Compilation timeout (30 seconds)"
        print(f"❌ {error_msg}")
        return False, error_msg, -1
        
    except Exception as e:
        error_msg = f"Compilation error: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg, -1


def regenerate_test_with_error_feedback(method_FEN, cfg_path_no, openai_key, error_log, test_code):
    """
    基于编译错误信息重新生成测试代码，使用 Code_Fixer prompt
    
    Args:
        method_FEN: 方法的完全限定名
        cfg_path_no: CFG路径编号
        openai_key: OpenAI API密钥
        error_log: 编译错误日志
        test_code: 原始测试代码
    
    Returns:
        str: 重新生成的测试代码
    """
    
    # 使用 Code_Fixer prompt 构建代码修复提示
    code_refinement_prompt = construct_code_refinement_prompt(error_log, test_code)
    
    print("🔧 Regenerating test code with Code_Fixer prompt...")
    
    try:
        regenerated_code = LLM_Utils.trigger_GPT_API_basedon_http_request(
            code_refinement_prompt, 
            model=Config.foundation_model_gpt4o_mini, 
            openai_key=openai_key
        )
        return regenerated_code
    except Exception as e:
        print(f"❌ Error during regeneration: {e}")
        return None


def generate_unit_tests_for_a_method(method_FEN, openai_key, project_dir, package_name, classpath_file=None, max_retries=3):
    """
    为指定方法的所有CFG路径生成单元测试，包含编译验证和错误修复
    
    Args:
        method_FEN: 方法的完全限定名
        openai_key: OpenAI API密钥
        project_dir: 项目目录
        package_name: 包名
        classpath_file: classpath文件路径
        max_retries: 每个CFG路径的最大重试次数
    """
    
    all_cfg_paths_num = len(Neo4jCommands.find_post_entities_in_relation(method_FEN, relation='Has_CFG_Path'))
    method_start_time = time.time()
    
    successful_tests = 0
    failed_tests = 0
    
    print(f"🚀 Generating tests for method: {method_FEN}")
    print(f"📊 Total CFG paths: {all_cfg_paths_num}")
    print("=" * 80)
    
    for cfg_path_no in range(1, all_cfg_paths_num + 1):
        print(f"\n📝 Processing CFG Path {cfg_path_no}/{all_cfg_paths_num}")
        print("-" * 60)
        
        compilation_success = False
        retry_count = 0
        
        while not compilation_success and retry_count < max_retries:
            try:
                start_time = time.time()
                
                # 生成测试代码
                if retry_count == 0:
                    print(f"🎯 Generating initial test code...")
                    test_gen_prompt = construct_prompt_for_a_cfg_path(method_FEN, cfg_path_no, openai_key)
                    test_code = LLM_Utils.trigger_GPT_API_basedon_http_request(
                        test_gen_prompt, 
                        model=Config.foundation_model_gpt4o_mini, 
                        openai_key=openai_key
                    )
                else:
                    print(f"🔄 Retry {retry_count}/{max_retries - 1}: Regenerating with error feedback...")
                    test_code = regenerate_test_with_error_feedback(
                        method_FEN, cfg_path_no, openai_key, last_error_log, test_code_after_formatting
                    )
                    if not test_code:
                        print("❌ Failed to regenerate test code")
                        break
                
                generation_time = time.time() - start_time
                print(f"⏱️  Generation time: {generation_time:.2f} seconds")
                
                # 保存测试文件
                saved_path, test_code_after_formatting = save_test_code_to_file(
                    test_code, method_FEN, cfg_path_no, project_dir, package_name
                )
                # print(f"💾 Saved to: {saved_path}")
                
                # 编译验证
                compile_start = time.time()
                success, error_log, exit_code = compile_test_file(
                    saved_path, project_dir, classpath_file
                )
                compile_time = time.time() - compile_start
                # print(f"⏱️  Compilation time: {compile_time:.2f} seconds")
                
                if success:
                    compilation_success = True
                    successful_tests += 1
                    total_time = time.time() - start_time
                    # print(f"✅ CFG Path {cfg_path_no} completed successfully!")
                    print(f"⏱️  Total time for this path: {total_time:.2f} seconds")
                    
                    # 打印存储路径和测试代码
                    print(f"📁 Test file saved to: {saved_path}")
                    print(f"📝 Generated test code:")
                    print("=" * 80)
                    print(test_code_after_formatting)
                    print("=" * 80)
                else:
                    retry_count += 1
                    last_error_log = error_log
                    
                    if retry_count < max_retries:
                        print(f"🔄 Test failed, retrying... ({retry_count}/{max_retries - 1})")
                    else:
                        print(f"❌ CFG Path {cfg_path_no} failed after {max_retries} attempts")
                        failed_tests += 1
                        # 保存失败的测试代码和错误日志以供调试
                        error_file = saved_path.replace('.java', '_error.txt')
                        with open(error_file, 'w') as f:
                            f.write(f"Final error log:\n{error_log}\n\n")
                            f.write(f"Final test code:\n{test_code_after_formatting}")
                        print(f"📋 Error details saved to: {error_file}")
                
            except Exception as e:
                retry_count += 1
                print(f"❌ Unexpected error: {e}")
                if retry_count >= max_retries:
                    failed_tests += 1
                    break

    # 总结报告
    method_end_time = time.time()
    total_method_time = method_end_time - method_start_time
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY REPORT")
    print("=" * 80)
    print(f"🎯 Method: {method_FEN}")
    print(f"📈 Total CFG paths: {all_cfg_paths_num}")
    # print(f"✅ Successful tests: {successful_tests}")
    # print(f"❌ Failed tests: {failed_tests}")
    # print(f"📊 Success rate: {(successful_tests/all_cfg_paths_num)*100:.1f}%")
    print(f"⏱️  Total time: {total_method_time:.2f} seconds")
    print(f"⏱️  Average time per path: {total_method_time/all_cfg_paths_num:.2f} seconds")
    print("=" * 80)


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description='Generate path-sensitive unit tests with compilation verification')
    parser.add_argument('--method', '-m', 
                       type=str, 
                       required=True,
                       help='Method FEN to generate tests for (e.g., org.apache.commons.lang3.StringUtils.compare(String,String,boolean))')
    parser.add_argument('--project-dir', '-d',
                       type=str,
                       required=True,
                       help='Project directory path')
    parser.add_argument('--package', '-p',
                       type=str,
                       required=True,
                       help='Package name (e.g., org.apache.commons.lang3)')
    parser.add_argument('--classpath-file', '-c',
                       type=str,
                       help='Path to classpath file (optional)')
    parser.add_argument('--max-retries', '-r',
                       type=int,
                       default=3,
                       help='Maximum retry attempts per CFG path (default: 3)')
    
    args = parser.parse_args()
    
    # 验证项目目录
    if not os.path.exists(args.project_dir):
        print(f"❌ Error: Project directory does not exist: {args.project_dir}")
        sys.exit(1)
    
    # 验证classpath文件（如果提供）
    if args.classpath_file and not os.path.exists(args.classpath_file):
        print(f"❌ Error: Classpath file does not exist: {args.classpath_file}")
        sys.exit(1)
    
    try:
        generate_unit_tests_for_a_method(
            method_FEN=args.method,
            openai_key=Config.openai_key,
            project_dir=args.project_dir,
            package_name=args.package,
            classpath_file=args.classpath_file,
            max_retries=args.max_retries
        )
    except Exception as e:
        print(f"❌ Error during test generation: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()