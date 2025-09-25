package com;

import java.io.IOException;
import java.io.File;


public class Code_Mining {
    public static void main(String[] args) throws IOException {
        // 检查命令行参数
        if (args.length != 2) {
            System.out.println("Usage: java Code_Mining <project_name> <package_name>");
            System.out.println("Example: java Code_Mining commons-lang-master org.apache.commons.lang3");
            System.out.println("Available projects should be in: " + Config.BASE_DIR + "/saved_data/Project/");
            return;
        }

        String projectName = args[0];
        String packageName = args[1];
        
        // 动态构建路径
        String projectBasicDir = Config.BASE_DIR + "/saved_data/Project/" + projectName;
        String projectSrcDir = "/src/main/java/" + packageName.replace('.', '/');
        String projectClassDir = "/target/classes/";
        
        // 检查项目目录是否存在
        File projectDir = new File(projectBasicDir);
        if (!projectDir.exists()) {
            System.err.println("Error: Project directory does not exist: " + projectBasicDir);
            System.err.println("Please make sure the project is available in: " + Config.BASE_DIR + "/saved_data/Project/");
            return;
        }
        
        // 检查源码目录是否存在
        File srcDir = new File(projectBasicDir + projectSrcDir);
        if (!srcDir.exists()) {
            System.err.println("Error: Source directory does not exist: " + projectBasicDir + projectSrcDir);
            System.err.println("Please check if the package name is correct: " + packageName);
            return;
        }
        
        System.out.println("=== Code Mining Started ===");
        System.out.println("Project: " + projectName);
        System.out.println("Package: " + packageName);
        System.out.println("Project Dir: " + projectBasicDir);
        System.out.println("Source Dir: " + projectBasicDir + projectSrcDir);
        
        // 创建输出目录
        String outputDir = Config.Experiment_Result_Basic_Dir + '/' + packageName.replace('.', '_');
        File outputDirFile = new File(outputDir);
        if (!outputDirFile.exists()) {
            outputDirFile.mkdirs();
            System.out.println("Created output directory: " + outputDir);
        }

        // AST分析
        System.out.println("\n=== Starting AST Analysis ===");
        String projectDirFull = projectBasicDir + projectSrcDir;
        String outputCsv = outputDir + "/ASTBased_Results.csv";
        String ASTerrorLogPath = outputDir + "/ast_based_analysis_error_log.txt";

        AST_Based_Analyzer.handle_all_java_files_in_a_directory(projectDirFull, outputCsv, ASTerrorLogPath);
        System.out.println("AST Analysis completed. Results saved to: " + outputCsv);

        // 字节码分析
        System.out.println("\n=== Starting Bytecode Analysis ===");
        String project_classes_dir = projectBasicDir + projectClassDir;
        String outputCsvPath = outputDir + "/ByteBased_Results.csv";
        String ByteerrorLogPath = outputDir + "/byte_based_analysis_error_log.txt";
        
        // 检查class目录是否存在
        File classDir = new File(project_classes_dir);
        if (!classDir.exists()) {
            System.err.println("Warning: Class directory does not exist: " + project_classes_dir);
            System.err.println("Please compile the project first using: mvn compile");
        } else {
            Sootup_Based_Analyzer.extract_info_from_all_classes_in_a_project(project_classes_dir, outputCsvPath, ByteerrorLogPath);
            System.out.println("Bytecode Analysis completed. Results saved to: " + outputCsvPath);
        }
        
        System.out.println("\n=== Code Mining Completed ===");
        System.out.println("All results saved to: " + outputDir);
    }
}
