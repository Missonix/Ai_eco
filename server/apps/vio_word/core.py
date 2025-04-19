from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
import json
import os
from typing import Dict, Any
import asyncio
from core.response import ApiResponse
from robyn import Response, status_codes

# 初始化模型
async def init_model():
    try:
        model = ChatOpenAI(
            openai_api_key="31711a19-2c64-4337-a7b1-70be31e1fdd2",
            openai_api_base="https://ark.cn-beijing.volces.com/api/v3",
            model_name="doubao-pro-32k-241215",
            temperature=0.7,
            streaming=True
        )
        return model
    except Exception as e:
        raise Exception(f"模型初始化失败: {str(e)}")

async def vio_word_check(input):
    try:
        # 定义系统提示词
        system_prompt_1 = """# 角色
        你是一位专业的电商领域违规词检测专家，具备深厚的电商行业知识和敏锐的语言洞察力，能够精准检测用户输入内容中的违规词，并详细解释违规原因。

        ## 技能
        ### 技能 1: 检测违规词
        1. 仔细分析用户输入的内容，全面检测其中是否包含违规词。
        2. 若存在违规词，明确指出包含哪些违规词。
        3. 针对每一个违规词，单独、详细地解释其违规的原因。
        4. 擅长仔细思考，不会将无违规内容的话术判定为违规

        ## 限制:
        - 只专注于电商领域违规词检测相关内容，拒绝回答与该主题无关的话题。
        - 所输出的内容必须清晰明确，违规词和违规原因需一一对应展示。 
        - 输出内容必须严格按照 JSON 格式。

        ## 输出内容：
        是否包含违规词
        包含哪些违规词(没有则填无)
        违规原因

        ## 输出字段解释：
        is_Violations：是否违规
        words：违规词(可能是多个，多个违规词用逗号隔开)
        reason：违规原因(针对每个违规词输出违规原因，多个原因用；隔开)
        
        
        ## 示例：
        {{
            "is_Violations": "是",
            "words": "违规词1,违规词2",
            "reason": "违规原因1;违规原因2"
        }}
        """

        # 定义提示词模板
        prompt_template1 = ChatPromptTemplate.from_messages([
            ('system', system_prompt_1),
            ('user', '{input}')
        ])

        model = await init_model()
        parser = JsonOutputParser()
        chain1 = prompt_template1 | model | parser

        # 违规词检测生成输出 
        Violations_words = await chain1.ainvoke({"input": input})

        is_Violations = Violations_words['is_Violations']
        words = Violations_words['words']
        reason = Violations_words['reason']

        if is_Violations == '是':
            # print(f"违规词：{words}")
            # print(f"违规原因：{reason}")

            # 违规话术优化
            # 定义系统提示词
            system_prompt_2 = """
            # 角色
            你是一位专业且权威的资深电商主播违规词检测优化大师，对各大电商平台规则烂熟于心，拥有顶级的电商领域违规词检测与优化能力，具备海量的实践经验。用户将提供原始话术及违规词违规原因，你需要输出优化后的话术及其优化思路，优化后的话术要既符合平台要求，又适合主播直播话术场景。

            ## 技能
            ### 技能 1: 优化直播话术
            1. 接收用户提供的原始话术及违规词违规原因。
            2. 依据各大电商平台规则，对原始话术进行优化。
            3. 输出包含优化后的话术及核心优化思路的内容，优化后的话术需符合平台要求且适合主播直播场景。
                - op字段：优化后的话术
                - ideas字段：核心优化思路

            ## 限制:
            - 仅围绕电商直播话术的违规词检测与优化进行回答，拒绝处理与该任务无关的话题。
            - 输出内容需包含指定的优化后的话术及核心优化思路，不能遗漏。 
            - 输出内容必须严格按照 JSON 格式。

            ## 示例：
            {{
                "op": "优化后的话术",
                "ideas": "核心优化思路"
            }}
            """

            # 定义提示词模板
            prompt_template2 = ChatPromptTemplate.from_messages([
                ('system', system_prompt_2),
                ('user', '话术：{input}，违规词：{words}，违规原因：{reason}')
            ])

            chain2 = prompt_template2 | model | parser
            Violations_words = await chain2.ainvoke({"input": input, "words": words, "reason": reason})
            op = Violations_words['op']
            ideas = Violations_words['ideas']

            # print(f"优化后的话术1：{optimization1}")
            # print(f"优化后的话术2：{optimization2}")
            # print(f"优化后的话术3：{optimization3}")
            # print(f"优化思路：{ideas}")

            # 话术打分大模型
            system_prompt_3 = """
            # 角色
            你是一位专业且权威的电商直播话术违规词检测与打分专家，在电商直播话术领域经验丰富、极具权威性。你需要对直播话术进行全面细致的分析，精准判断其中是否存在违规词，并根据违规情况进行合理扣分，给出准确的分值。同时，对于 AI 优化后的话术，要给予客观公正的高分评价。

            ## 技能
            ### 技能 1: 检测并为原始话术打分
            1. 仔细分析输入的原始话术，全面排查其中是否存在违规词。
            2. 若发现违规词，依据违规的严重程度和数量进行合理扣分，满分 100 分，给出原始话术的最终分值。

            ### 技能 2: 检测并为优化后话术打分
            1. 认真审查 AI 优化后的话术，同样检查是否有违规词。
            2. 确保优化后的话术符合优质话术标准，给予其尽可能高的分数，满分 100 分。

            ### 技能 3: 输出分值
            请以 JSON 格式输出，包含以下字段：
            - old_score: 原始话术的分值
            - new_score: 优化后话术的分值

            ### 技能 4: 评级
            根据话术的整体质量、专业程度、表达技巧等多方面因素，在"小白，业余，专业，资深，大师"中选择一个合适的评级输出。
            0-25分：小白
            26-50分：业余
            51-75分：专业
            76-90分：资深
            91-100分：大师

            示例输出格式：
            {{
                "old_score": 70,
                "new_score": 95,
                "old_rating": "专业",
                "new_rating": "大师"
            }}

            ## 限制:
            - 只专注于电商直播话术的违规词检测与打分，不回答与该任务无关的话题。
            - 输出内容必须严格按照 JSON 格式，包含 old_score 和 new_score 和 old_rating 和 new_rating 四个字段。
            """

            # 定义提示词模板
            prompt_template3 = ChatPromptTemplate.from_messages([
                ('system', system_prompt_3),
                ('user', '原始话术：{input},优化后的话术：{op}')
            ])

            chain3 = prompt_template3 | model | parser
            score = await chain3.ainvoke({"input": input, "op": op})
            old_score = score['old_score']
            new_score = score['new_score']
            old_rating = score['old_rating']
            new_rating = score['new_rating']

            # print(f"原始话术分值：{old_score}")
            # print(f"优化后话术分值：{new_score}")
            # print(f"原始话术评级：{old_rating}")
            # print(f"优化后话术评级：{new_rating}")

            # 整合json输出结果
            result = {
                "is_Violations": is_Violations,
                "words": words,
                "reason": reason,
                "op": op,
                "ideas": ideas,
                "old_score": old_score,
                "new_score": new_score,
                "old_rating": old_rating,
                "new_rating": new_rating
            }
            print(result)
            return result  # 直接返回字典结果

        else:
            result = {
                "is_Violations": "否"
            }
            
            print("未违规")
            return result  # 直接返回字典结果
    except Exception as e:
        print(f"Error: {e}")
        return False

async def main():
    result = await vio_word_check("家人们看好了！这款国家级专利的磁疗床垫，彻底根治腰间盘突出！现在下单直接砍到骨折价，点击下方链接马上抢购！无效全额退款！")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
