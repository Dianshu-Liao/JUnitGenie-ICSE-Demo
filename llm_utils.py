import requests
import os

class LLM_Utils:


    # @staticmethod
    # def trigger_GPT_API_basedon_http_request(message, model, openai_key, temperature=0):
    #     # url = "https://api.openai.com/v1/chat/completions"
    #     url = "https://openkey.cloud/v1/chat/completions"

    #     headers = {
    #         'Content-Type': 'application/json',
    #         # 填写OpenKEY生成的令牌/KEY，注意前面的 Bearer 要保留，并且和 KEY 中间有一个空格。
    #         'Authorization': 'Bearer {}'.format(openai_key)
    #     }

    #     data = {
    #         "model": model,
    #         "messages": message,
    #         "temperature": temperature,
    #         "top_p": 1,
    #         "frequency_penalty": 0,
    #         "presence_penalty": 0,
    #     }

    #     response = requests.post(url, headers=headers, json=data)
    #     # print("Status Code", response.status_code)
    #     if response.status_code != 200:
    #         raise ValueError("Failed to get response")
    #     return response.json()['choices'][0]['message']['content']

    @staticmethod
    def trigger_GPT_API_basedon_http_request(message, model, openai_key, temperature=0):
        """
        使用官方 OpenAI API 发送请求获取 GPT 响应
        
        Args:
            message (list): 消息列表，包含 role 和 content
            model (str): 使用的模型名称 (如 'gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo')
            openai_key (str): OpenAI API 密钥
            temperature (float): 控制响应的随机性 (0-2，默认0)
        
        Returns:
            str: GPT 生成的响应内容
            
        Raises:
            ValueError: API 请求失败时抛出异常
        """
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {openai_key}'
        }

        data = {
            "model": model,
            "messages": message,
            "temperature": temperature,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code != 200:
                error_detail = ""
                try:
                    error_detail = response.json().get('error', {}).get('message', 'Unknown error')
                except:
                    error_detail = response.text
                raise ValueError(f"OpenAI API request failed with status {response.status_code}: {error_detail}")
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            raise ValueError("OpenAI API request timed out (60 seconds)")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Network error when calling OpenAI API: {str(e)}")
        except KeyError as e:
            raise ValueError(f"Unexpected response format from OpenAI API: missing {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error when calling OpenAI API: {str(e)}")


    @staticmethod
    def read_prompt_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()


    @staticmethod
    def get_example_subdirectories(directory):
        """
        Get all subdirectories in the specified directory that start with 'Example'.

        Parameters:
            directory (str): The path to the directory to search.

        Returns:
            list: A list of subdirectory names starting with 'Example'.
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"The specified directory does not exist: {directory}")

        return [
            subdir for subdir in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, subdir)) and subdir.startswith("Example")
        ]

    @staticmethod
    def read_example_prompts(prompt_dir):
        example_prompt = []
        example_dirs = LLM_Utils.get_example_subdirectories(prompt_dir)

        for example_dir in example_dirs:
            example_input_prompt_file = prompt_dir + '/' + example_dir + '/Input'
            example_output_prompt_file = prompt_dir + '/' + example_dir + '/Output'

            example_input_prompt = LLM_Utils.read_prompt_file(example_input_prompt_file)
            example_output_prompt = LLM_Utils.read_prompt_file(example_output_prompt_file)
            example_user = {'role': 'user', 'content': example_input_prompt}
            example_assistant = {'role': 'assistant', 'content': example_output_prompt}
            example_prompt.append(example_user)
            example_prompt.append(example_assistant)
        return example_prompt

