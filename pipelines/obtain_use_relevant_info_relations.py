import pandas as pd
import re
import tqdm
from config import Config



'''
def obtain_relevant_info(df, cfg_path, method_sub_signature):
    relevant_fields = []
    relevant_methods = []

    relevant_info = ''

    # get all nodes in the cfg_path
    # Regular expression to match CFG nodes
    node_pattern = re.compile(r'"(\d+)" \[label="(.+?)"\];')

    # Extract nodes and their content
    cfg_nodes = node_pattern.findall(cfg_path)

    method_info = []

    # 正则表达式
    pattern = r"&lt;(.+?): (.+?)&gt;"
    found_class_method = set()

    for node in cfg_nodes:
        node_content = node[1]
        # # 检查是否包含 staticinvoke 或 virtualinvoke (relevant method info)
        # if "staticinvoke" in node_content or "virtualinvoke" in node_content:
        #     match = re.search(pattern, node_content)
        #     if match:
        #         class_name = match.group(1)  # 方法所属的类
        #         method_signature = match.group(2)  # 方法的完整签名
        #         method_info.append((class_name, method_signature))
        #
        #         # avoid calling the method itself
        #         if method_signature == method_sub_signature:
        #             continue
        #
        #         # avoid multiple times of the same method
        #         if class_name + '.' + method_signature in found_class_method:
        #             continue
        #         matched_method_in_df = df[(df['class_name'] == class_name) & (df['sub_signature'] == method_signature)]
        #         if len(matched_method_in_df) == 0:
        #             print(f"Method not found in the dataframe: {class_name}, {method_signature}")
        #         else:
        #             print(f"Method found in the dataframe: {class_name}, {method_signature}")
        #             method_source_code = matched_method_in_df['source_code'].values[0]
        #             found_class_method.add(class_name + '.' + method_signature)
        #
        #             relevant_info += f"Class Name: {class_name}\n"
        #             relevant_info += f"Method Signature: {method_signature}\n"
        #             relevant_info += f"Method Source Code: {method_source_code}\n\n"

        match = re.search(pattern, node_content)
        if match:
            class_name = match.group(1)  # 方法所属的类
            method_signature = match.group(2)  # 方法的完整签名
            method_info.append((class_name, method_signature))

            # avoid calling the method itself
            if method_signature == method_sub_signature:
                continue

            # avoid multiple times of the same method
            if class_name + '.' + method_signature in found_class_method:
                continue
            matched_method_in_df = df[(df['class_name'] == class_name) & (df['sub_signature'] == method_signature)]
            if len(matched_method_in_df) == 0:
                print(f"Method not found in the dataframe: {class_name}, {method_signature}")
            else:
                print(f"Method found in the dataframe: {class_name}, {method_signature}")
                source_code = matched_method_in_df['source_code'].values[0]
                found_class_method.add(class_name + '.' + method_signature)

                element_type = matched_method_in_df['type'].values[0]
                element_signature = matched_method_in_df['sub_signature'].values[0]


                relevant_info += f"Class Name: {class_name}\n"
                relevant_info += f"Type: {element_type}\n"
                relevant_info += f"Signature: {element_signature}\n"
                relevant_info += f"Source Code: {source_code}\n\n"

        # relevant fields info

    return relevant_info

'''


def simplify_method_parameters(sub_signature_or_name):
    # 提取方法名和参数部分
    match = re.match(r'([\w<>]+)\((.*?)\)', sub_signature_or_name)
    if not match:
        # 如果输入格式不符合方法签名，则直接返回原字符串
        return sub_signature_or_name

    method_name = match.group(1)  # 方法名
    parameters = match.group(2)  # 参数部分

    if not parameters.strip():
        # 如果参数为空（如 `methodName()`），直接返回
        return f"{method_name}()"

    # 将参数部分按逗号分割并处理每个参数
    simplified_parameters = []
    for param in parameters.split(','):
        # 去掉空格并提取简单类名（最后一个"."之后的部分）
        simple_name = param.strip().split('.')[-1]
        simple_name = simple_name.split('$')[-1]
        simplified_parameters.append(simple_name)

    # 重新拼接方法名和简化后的参数
    simplified_signature = f"{method_name}({','.join(simplified_parameters)})"
    return simplified_signature


def obtain_relevant_info(field_entities, enum_constant_entities, method_entities, cfg_path, project_package_name):
    field_and_enum_constant_entities = pd.concat([field_entities, enum_constant_entities], ignore_index=True)
    relevant_fields_and_enum_constants = []
    relevant_methods = []

    node_pattern = re.compile(r'"(\d+)" \[label="(.+?)"\];')
    pattern = re.compile(
        r"(?:\$[\w\d]+ = )?"  # 可选的变量部分（如 $stack9 = ）
        r"<([\w.$]+):\s+([\w\[\].<>]+)\s+([\w<>]+(?:\(.*?\))?)>"  # 提取 FQN、返回类型、签名
    )

    # Extract nodes and their content
    cfg_nodes = node_pattern.findall(cfg_path)
    for node in cfg_nodes:
        node_content = node[1]

        # Match methods or fields in the node content
        matches = pattern.findall(node_content)

        for match in matches:
            # fqn = match.group(1)  # Fully Qualified Name
            # type_or_return = match.group(2)  # Type for fields or return type for methods
            # sub_signature_or_name = match.group(3)  # Sub-signature (for methods) or field name
            class_fqn, type_or_return, sub_signature_or_name = match

            # Determine if it's a method or field
            if "(" in sub_signature_or_name and ")" in sub_signature_or_name:

                # This is a method
                if class_fqn.startswith(project_package_name):
                    # method_signature = simplify_method_parameters(sub_signature_or_name)
                    # FEN = fqn + '.' + method_signature
                    # if FEN in FEN_List:
                    #     relevant_methods.append(FEN)
                    simple_sub_signature = simplify_method_parameters(sub_signature_or_name)
                    relevant_method_FEN = f"{class_fqn}.{simple_sub_signature}"
                    corresponding_row = method_entities[method_entities['FEN:ID'] == relevant_method_FEN]



                    if len(corresponding_row) == 0:
                        pass
                    elif len(corresponding_row) == 1:
                        FEN = corresponding_row.iloc[0]['FEN:ID']
                        relevant_methods.append(FEN)
                    else:
                        raise ValueError(f"Method FEN: {relevant_method_FEN} has more than one row!")
                        # FEN = corresponding_row.iloc[0]['FEN:ID']
                        # relevant_methods.append(FEN)
                        # print('FEN: {} more than one row!'.format(FEN))
            else:
                # # This is a field
                # if fqn.startswith(project_package_name):
                #     FEN = fqn + '.' + sub_signature_or_name
                #     if FEN in FEN_List:
                #         relevant_fields.append(FEN)
                relevant_field_FEN = f"{class_fqn}.{sub_signature_or_name}"
                corresponding_row = field_and_enum_constant_entities[field_and_enum_constant_entities['FEN:ID'] == relevant_field_FEN]

                if len(corresponding_row) == 0:
                    pass
                elif len(corresponding_row) == 1:
                    FEN = corresponding_row.iloc[0]['FEN:ID']
                    relevant_fields_and_enum_constants.append(FEN)
                else:
                    raise ValueError(f"Field or Enum Constant FEN: {relevant_field_FEN} has more than one row!")
                    # FEN = corresponding_row.iloc[0]['FEN']
                    # relevant_fields.append(FEN)
                    # print('FEN: {} more than one row!'.format(FEN))

    return list(set(relevant_fields_and_enum_constants)), list(set(relevant_methods))




def uses_field_method_relations_construction():
    dict_uses_field_relations = {'FEN:START_ID': [], 'FEN:END_ID': [], ':TYPE': []}
    dict_uses_enum_constant_relations = {'FEN:START_ID': [], 'FEN:END_ID': [], ':TYPE': []}
    dict_uses_method_relations = {'FEN:START_ID': [], 'FEN:END_ID': [], ':TYPE': []}

    field_entities = pd.read_csv(Config.field_entities_path)
    enum_constant_entities = pd.read_csv(Config.enum_constant_entities_path)
    method_entities = pd.read_csv(Config.method_entities_path)
    cfg_path_entities = pd.read_csv(Config.cfg_path_entities_path)

    for index, row in tqdm.tqdm(cfg_path_entities.iterrows(), total=len(cfg_path_entities)):
        cfg_path = row['CFG_Path'].replace('\\n', '\n')
        cfg_path_FEN = row['FEN:ID']

        relevant_fields_and_enum_constants, relevant_methods = obtain_relevant_info(field_entities, enum_constant_entities, method_entities, cfg_path,
                                                                 Config.project_package_name)
        for relevant_fields_and_enum_constants_FEN in relevant_fields_and_enum_constants:
            if relevant_fields_and_enum_constants_FEN in field_entities['FEN:ID'].values:
                dict_uses_field_relations['FEN:START_ID'].append(cfg_path_FEN)
                dict_uses_field_relations['FEN:END_ID'].append(relevant_fields_and_enum_constants_FEN)
                dict_uses_field_relations[':TYPE'].append('Uses_Field')
            elif relevant_fields_and_enum_constants_FEN in enum_constant_entities['FEN:ID'].values:
                dict_uses_enum_constant_relations['FEN:START_ID'].append(cfg_path_FEN)
                dict_uses_enum_constant_relations['FEN:END_ID'].append(relevant_fields_and_enum_constants_FEN)
                dict_uses_enum_constant_relations[':TYPE'].append('Uses_Enum_Constant')

        for relevant_method_FEN in relevant_methods:
            dict_uses_method_relations['FEN:START_ID'].append(cfg_path_FEN)
            dict_uses_method_relations['FEN:END_ID'].append(relevant_method_FEN)
            dict_uses_method_relations[':TYPE'].append('Uses_Method')

    df_uses_field_relations = pd.DataFrame(dict_uses_field_relations)
    df_use_enum_constant_relations = pd.DataFrame(dict_uses_enum_constant_relations)

    df_uses_method_relations = pd.DataFrame(dict_uses_method_relations)

    df_uses_field_relations.to_csv(Config.uses_field_relations_path, index=False)
    df_use_enum_constant_relations.to_csv(Config.uses_enum_constant_relations_path, index=False)
    df_uses_method_relations.to_csv(Config.uses_method_relations_path, index=False)





if __name__ == '__main__':


    #
    # project_package_name = 'org.apache.commons.lang3'
    # field_entities_path = 'saved_data/project_information/org_apache_commons_lang3/Entities/field_entities.csv'
    # enum_constant_entities_path = 'saved_data/project_information/org_apache_commons_lang3/Entities/enum_constant_entities.csv'
    # method_entities_path = 'saved_data/project_information/org_apache_commons_lang3/Entities/method_level_entities.csv'
    # cfg_path_entities_path = 'saved_data/project_information/org_apache_commons_lang3/Entities/cfg_path_entities.csv'
    # uses_field_relations_path = 'saved_data/project_information/org_apache_commons_lang3/Relations/uses_field.csv'
    # uses_method_relations_path = 'saved_data/project_information/org_apache_commons_lang3/Relations/uses_method.csv'
    # uses_enum_constant_relations_path = 'saved_data/project_information/org_apache_commons_lang3/Relations/uses_enum_constant.csv'

    uses_field_method_relations_construction()