# JUnitGenie Tool

A path-sensitive unit test generation tool that leverages knowledge distillation and control flow graph (CFG) analysis to generate high-quality JUnit tests for Java projects.

## Overview

JUnitGenie Tool is a two-stage test generation framework:
1. **Context Knowledge Extraction**: Extract code-aware knowledge from Java projects and build a knowledge graph
2. **Path-Sensitive Generation**: Generate unit tests for specific CFG paths with compilation verification

## Prerequisites

- Python 3.12
- Java 8
- Maven (for Java project management)
- Neo4j database (for knowledge graph storage)
- **OpenAI API key** (for LLM-based test generation)
  - Official OpenAI API account with available credits
  - API key with access to GPT models (gpt-4o-mini, gpt-4, etc.)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd JUnitGenie_Tool
```


2. Configure your OpenAI API key in `config.py`:
```python
openai_key = "your-key-here"
```

4. Ensure Neo4j is installed and running on your system.

## Quick Start

Here's a complete example using the Apache Commons Lang3 project:

```bash
# Step 1: Prepare your Java project
ls saved_data/Project
cd ProjectInfoExtraction

# Step 2: Extract project information
mvn exec:java -Dexec.mainClass="com.Code_Mining" -Dexec.args="commons-lang-master org.apache.commons.lang3"

# Step 3: Extract context knowledge
cd ..
python pipelines/extract_code_aware_knowledge.py --package org.apache.commons.lang3

# Step 4: Import knowledge to Neo4j
bash saved_data/Code_Knowledge_Base/org_apache_commons_lang3/neo4j_import_command.txt

# Step 5: Generate path-sensitive tests
python pipelines/path_sensitive_generation.py \
  --method "org.apache.commons.lang3.StringUtils.compare(String,String,boolean)" \
  --project-dir "saved_data/Project/commons-lang-master" \
  --package "org.apache.commons.lang3"

# Step 6: Run the generated tests
cd saved_data/Project/commons-lang-master
mvn test
```

## Detailed Usage

### Step 1: Context Knowledge Extraction

This step analyzes your Java project and extracts code-aware knowledge including classes, methods, fields, and their relationships.

#### 1.1 Project Analysis

First, analyze your Java project to extract AST and bytecode information:

```bash
cd ProjectInfoExtraction
mvn exec:java -Dexec.mainClass="com.Code_Mining" -Dexec.args="<project-name> <package-name>"
```

**Parameters:**
- `<project-name>`: Name of your Java project (should be in `saved_data/Project/`)
- `<package-name>`: Root package name to analyze (e.g., `org.apache.commons.lang3`)

**Example:**
```bash
mvn exec:java -Dexec.mainClass="com.Code_Mining" -Dexec.args="commons-lang-master org.apache.commons.lang3"
```

This will generate analysis results in `saved_data/Code_Knowledge_Base/<package_name>/`:
- `ASTBased_Results.csv`: AST analysis results
- `ByteBased_Results.csv`: Bytecode analysis results

#### 1.2 Knowledge Graph Construction

Extract code-aware knowledge and prepare Neo4j import commands:

```bash
cd ..  # Back to project root
python pipelines/extract_code_aware_knowledge.py --package <package-name>
```

**Parameters:**
- `--package`, `-p`: Java package name to process (required)

**Example:**
```bash
python pipelines/extract_code_aware_knowledge.py --package org.apache.commons.lang3
```

This will:
1. Extract basic entities and relations
2. Extract CFG path entities and relations  
3. Construct usage relations
4. Generate Neo4j import commands

#### 1.3 Import to Neo4j Database

Execute the generated Neo4j import commands:

```bash
bash saved_data/Code_Knowledge_Base/<package_name_with_underscores>/neo4j_import_command.txt
```

**Example:**
```bash
bash saved_data/Code_Knowledge_Base/org_apache_commons_lang3/neo4j_import_command.txt
```

### Step 2: Path-Sensitive Generation

Generate unit tests for specific methods with path-sensitive analysis and automatic compilation verification.

#### 2.1 Generate Tests

```bash
python pipelines/path_sensitive_generation.py \
  --method "<method-FEN>" \
  --project-dir "<project-directory>" \
  --package "<package-name>" \
  [--max-retries <number>]
```

**Parameters:**
- `--method`, `-m`: Method Fully Qualified Name (FEN) to generate tests for (required)
- `--project-dir`, `-d`: Path to the Java project directory (required)
- `--package`, `-p`: Java package name (required)
- `--max-retries`, `-r`: Maximum retry attempts for failed compilations (default: 3)

**Example:**
```bash
python pipelines/path_sensitive_generation.py \
  --method "org.apache.commons.lang3.StringUtils.compare(String,String,boolean)" \
  --project-dir "saved_data/Project/commons-lang-master" \
  --package "org.apache.commons.lang3" \
  --max-retries 2
```

#### 2.2 What Happens During Generation

For each CFG path of the target method:

1. **Context Analysis**: Retrieves relevant context from the knowledge graph
2. **Test Generation**: Uses LLM to generate path-specific test code
3. **Code Formatting**: Formats the test into executable JUnit code
4. **Compilation Verification**: Automatically compiles the test to check for errors
5. **Error Correction**: If compilation fails, uses Code_Fixer prompt to regenerate
6. **Result Reporting**: Shows success/failure status and execution times

#### 2.3 Generated Test Location

Tests are saved to:
```
<project-dir>/src/test/java/<package-path>/<MethodName>_cfg_path_<N>_Test.java
```

**Example:**
```
saved_data/Project/commons-lang-master/src/test/java/org/apache/commons/lang3/StringUtils_compare_String_String_boolean_cfg_path_1_Test.java
```

#### 2.4 Running Generated Tests

Navigate to your project directory and run Maven tests:

```bash
cd saved_data/Project/commons-lang-master
mvn test
```

Or run specific test classes:
```bash
mvn test -Dtest="StringUtils_compare_String_String_boolean_cfg_path_1_Test"
```

## Project Structure

```
JUnitGenie_Tool/
├── pipelines/
│   ├── extract_code_aware_knowledge.py    # Step 1: Knowledge extraction
│   ├── path_sensitive_generation.py       # Step 2: Test generation
│   ├── basic_entities_extraction.py       # Entity extraction
│   ├── obtain_cfg_paths.py               # CFG path analysis
│   ├── obtain_use_relevant_info_relations.py  # Usage relation construction
│   ├── context_knowledge_distillation.py  # Context knowledge retrieval
│   └── code_formatting.py                # Code formatting utilities
├── prompts/
│   ├── Code_Fixer/                       # Error correction prompts
│   ├── LLM_CFGPath/                      # CFG path generation prompts
│   └── ...                               # Other prompt templates
├── ProjectInfoExtraction/                 # Java analysis tools
├── saved_data/
│   ├── Project/                          # Java projects to analyze
│   └── Code_Knowledge_Base/              # Generated knowledge bases
├── config.py                            # Configuration settings
├── llm_utils.py                         # LLM interaction utilities
├── neo4jcommands.py                     # Neo4j database operations
└── utils.py                             # General utilities
```

## Configuration

### API Keys

Configure your OpenAI API key in `config.py`:

```python
class Config:
    openai_key = "sk-your-actual-openai-api-key-here"  # Official OpenAI API key
    foundation_model_gpt4o_mini = "gpt-4o-mini"  # Or your preferred model
```

**Getting an OpenAI API Key:**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new secret key
5. Copy the key (starts with `sk-`) and paste it in your config

**Cost Considerations:**
- API usage is pay-per-token
- GPT-4o-mini is more cost-effective than GPT-4
- Monitor your usage in the OpenAI dashboard

### Neo4j Settings

Ensure Neo4j is properly configured. The tool assumes default Neo4j installation paths. Modify the import commands in `extract_code_aware_knowledge.py` if your Neo4j installation differs.

### Classpath Configuration

The tool automatically detects `classpath.txt` in the project root. Ensure this file contains all necessary dependencies for compiling your tests.

## Features

### ✅ Core Features
- **Path-Sensitive Analysis**: Generate tests for each CFG path of a method
- **Automatic Compilation**: Verify generated tests compile successfully
- **Intelligent Error Correction**: Use specialized prompts to fix compilation errors
- **Knowledge Graph Integration**: Leverage extracted code knowledge for better test generation
- **Progress Reporting**: Detailed progress tracking and statistics

### ✅ Advanced Features
- **Retry Mechanism**: Automatic retry with error feedback for failed tests
- **Code Formatting**: Automatic formatting of generated test code
- **Classpath Detection**: Automatic detection of project dependencies
- **Multiple CFG Paths**: Handle methods with complex control flow

## Troubleshooting

### Common Issues

1. **"No CFG paths found"**: The method may not have complex control flow or may not be in the knowledge base
2. **Compilation errors**: Check that all dependencies are in `classpath.txt`
3. **Neo4j connection issues**: Ensure Neo4j is running and accessible
4. **API rate limits**: Configure multiple API keys or add delays between requests

### Debug Mode

For detailed output, you can modify the print statements in the generation scripts or check the error logs saved alongside generated tests.

## Examples

### Example 1: Simple Method
```bash
python pipelines/path_sensitive_generation.py \
  --method "org.apache.commons.lang3.StringUtils.isEmpty(CharSequence)" \
  --project-dir "saved_data/Project/commons-lang-master" \
  --package "org.apache.commons.lang3"
```

### Example 2: Complex Method with Multiple Paths
```bash
python pipelines/path_sensitive_generation.py \
  --method "org.apache.commons.lang3.StringUtils.compare(String,String,boolean)" \
  --project-dir "saved_data/Project/commons-lang-master" \
  --package "org.apache.commons.lang3" \
  --max-retries 3
```

### Example 3: Different Package
```bash
# First extract knowledge for the new package
python pipelines/extract_code_aware_knowledge.py --package com.example.myproject

# Then generate tests
python pipelines/path_sensitive_generation.py \
  --method "com.example.myproject.Utils.processData(String,int)" \
  --project-dir "saved_data/Project/my-project" \
  --package "com.example.myproject"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with a sample Java project
5. Submit a pull request

## License

[Specify your license here]

## Citation

If you use this tool in your research, please cite:

```bibtex
[Add your citation here]
```
