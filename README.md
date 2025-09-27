# JUnitGenie Tool

A path-sensitive unit test generation tool that leverages knowledge distillation and control flow graph (CFG) analysis to generate high-quality JUnit tests for Java projects.


## Prerequisites

- Python 3.12
- Java 8
- Maven (for Java project management)
- Neo4j database (for knowledge graph storage)
- OpenAI API key (for LLM-based test generation)
  - Official OpenAI API account with available credits
  - API key with access to GPT models (gpt-4o-mini, gpt-4, etc.)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Dianshu-Liao/JUnitGenie-ICSE-Demo.git
cd JUnitGenie_Tool
```


2. Configure your OpenAI API key in `config.py`:
```python
openai_key = "your-key-here"
```

## Quick Start

Here's a complete example using the Apache Commons Lang3 project:

```bash
# Step 1: Prepare your Java project and compile it
cd saved_data/Project/commons-lang-master 
mvn compile

# Step 2: Extract project information
cd ../../../ProjectInfoExtraction
mvn exec:java -Dexec.mainClass="com.Code_Mining" -Dexec.args="commons-lang-master org.apache.commons.lang3"

# Step 3: Extract context knowledge
cd ..
python pipelines/extract_code_aware_knowledge.py --package org.apache.commons.lang3

# Step 4: Import knowledge to Neo4j
bash saved_data/Code_Knowledge_Base/org_apache_commons_lang3/neo4j_import_command.txt
neo4j start

# Step 5: Generate path-sensitive tests
python pipelines/path_sensitive_generation.py \
  --method "org.apache.commons.lang3.StringUtils.compare(String,String,boolean)" \
  --project-dir "saved_data/Project/commons-lang-master" \
  --package "org.apache.commons.lang3"
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
