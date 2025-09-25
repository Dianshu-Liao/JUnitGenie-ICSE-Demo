package com;
import java.io.File;

public class Config {
    public static final String CURRENT_DIR = System.getProperty("user.dir");

    // 上一级目录（也就是你想要的 Basic_Dir）
    public static final String BASE_DIR = new File(CURRENT_DIR).getParent();

    public static String Experiment_Result_Basic_Dir = BASE_DIR + "/saved_data/Code_Knowledge_Base";

    public static String projectclassDir = "/target/classes/";

    public static String package_name = "org.apache.commons.lang3";

    // for commons-lang3
    public static String Project_Basic_Dir = BASE_DIR + "/saved_data/Project/commons-lang-master";
    public static String projectSrcDir = "/src/main/java/" + package_name.replace('.', '/');
    public static String testCodeDir = Project_Basic_Dir + "/src/test/java/" + package_name.replace('.', '/');
    public static String syntaxErrorLog = Experiment_Result_Basic_Dir + "/syntax_error_log.txt";


}
