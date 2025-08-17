#!/usr/bin/env python3
"""
全自动标题生成器 v4
支持自定义角色名字池，全自动随机生成标题
"""

import re
import random
import json
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
import sys

# 设置UTF-8输出
if sys.platform == "win32":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)


class AutoTitleGenerator:
    def __init__(
        self,
        name_file: str = "name.md",
        rules_file: str = "rules.md",
        character_pool_file: str = "characters.json",
    ):
        """初始化生成器"""
        self.vocabulary = self._load_vocabulary(name_file)
        self.rules_examples = self._load_rules_examples(rules_file)
        self.character_pool = self._load_character_pool(character_pool_file)

    def _load_vocabulary(self, file_path: str) -> Dict[str, List[str]]:
        """加载词汇库"""
        vocab = {}
        current_category = ""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("## "):
                        # 假设标题格式是 "## 中文名 英文名 & 其他"
                        # 我们只需要提取中文名部分作为字典键
                        match = re.match(r'##\s*([\u4e00-\u9fa5]+)', line)
                        if match:
                            current_category = match.group(1).strip()
                        else:
                            # 备用逻辑，如果正则匹配失败，回退到原来的逻辑，但会带英文后缀
                            # 进一步尝试只取第一个单词（中文），如果之前修改过的话
                            current_category = line[3:].split("&")[0].split(" ")[0].strip()
                        
                        vocab[current_category] = []
                    elif line.startswith("- ") and current_category:
                        word = line[2:].split(" (")[0].strip()
                        if word:
                            vocab[current_category].append(word)
        except FileNotFoundError:
            print(f"警告: 找不到文件 {file_path}")

        return vocab

    def _load_rules_examples(self, file_path: str) -> Dict[str, List[Dict]]:
        """加载规则示例"""
        examples = {}
        current_style = ""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("### 风格"):
                        current_style = line.split("：")[1].strip()
                        examples[current_style] = []
                    elif line.startswith("| ") and current_style and "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if (
                            len(parts) >= 3
                            and parts[1]
                            and parts[2]
                            and not parts[1].startswith("原标题")
                        ):
                            examples[current_style].append(
                                {"original": parts[1], "generated": parts[2]}
                            )
        except FileNotFoundError:
            print(f"警告: 找不到文件 {file_path}")

        return examples

    def _load_character_pool(self, file_path: str) -> Dict[str, List[str]]:
        """加载角色名字池"""
        default_pool = {
            "动漫角色": [
                "远坂凛", "saber", "亚丝娜", "楪祈", "御坂美琴", "炮姐", "时崎狂三", "五河琴里", "夜刀神十香", 
                "四糸乃", "八舞耶俱矢", "八舞夕弦", "诱宵美九", "或守鞠亚", "园神凛祢", "非莉娅", "两仪式", 
                "浅上藤乃", "黑桐鲜花", "苍崎青子", "久远寺有珠", "卡莲", "尤菲", "C.C.", "夏莉", "罗伊德", "柯内莉娅",
            ],
            "游戏角色": [
                "希尔薇", "莫妮卡", "星梨花", "艾莉卡", "千早", "亚里沙", "真白", "伊莉雅", "美游", "小黑", 
                "克洛伊", "巴泽特", "斯卡哈", "斯卡蒂", "布伦希尔德", "齐格飞", "齐格鲁德", "源赖光", "酒吞童子", 
                "茨木童子", "玉藻前", "清姬", "阎魔刀",
            ],
            "原创角色": [
                "苏沐沐", "林若曦", "慕容雪", "欧阳娜娜", "上官婉儿", "司马嫣然", "夏雨荷", "魏紫嫣", "秦雨瑶", 
                "唐婉儿", "宋佳音", "许清歌", "韩雪莉", "冯雨晴", "邓紫琪", "曹颖", "萧薰儿", "彩鳞", "云韵", 
                "美杜莎", "雅妃", "纳兰嫣然", "云芝", "小医仙",
            ],
            "通用称呼": [
                "学姐", "学妹", "老师", "护士", "医生", "警察", "空姐", "女仆", "兔女郎", "巫女", "修女", 
                "骑士", "法师", "牧师", "刺客", "弓箭手", "舞娘", "歌姬", "偶像", "主播", 
            ],
            "自定义角色": [ # 新增一个默认的空分类，以便用户直接添加
                "自定义角色1", "自定义角色2"
            ]
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                custom_pool = json.load(f)
                # 合并自定义池和默认池
                for category, characters in custom_pool.items():
                    if category in default_pool:
                        # 使用集合进行去重合并，保持原有顺序并添加新的
                        existing_chars = set(default_pool[category])
                        for char in characters:
                            if char not in existing_chars:
                                default_pool[category].append(char)
                                existing_chars.add(char)
                    else:
                        default_pool[category] = characters # 添加新分类
        except FileNotFoundError:
            # 如果文件不存在，创建默认的角色池文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_pool, f, ensure_ascii=False, indent=2)
            print(f"已创建默认角色池文件: {file_path}")
        except json.JSONDecodeError:
            print(f"警告: 角色池文件 {file_path} 格式错误，将使用默认角色池。")
            # 如果JSON文件损坏，也写入默认的
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_pool, f, ensure_ascii=False, indent=2)


        return default_pool

    def get_random_character(self) -> str:
        """从角色池中随机选择一个角色"""
        # 随机选择一个类别，确保类别非空
        available_categories = [cat for cat, chars in self.character_pool.items() if chars]
        if not available_categories:
            return "某人" # Fallback if no characters available

        category = random.choice(available_categories)
        # 从该类别中随机选择一个角色
        return random.choice(self.character_pool[category])

    def get_random_word(self, category: str, fallback: str = "") -> str:
        """从指定类别获取随机词汇"""
        if category in self.vocabulary and self.vocabulary[category]:
            return random.choice(self.vocabulary[category])
        return fallback

    def generate_style1(self, character: str = None) -> str:
        """风格1：神经刀第一人称"""
        # 随机选择角色（如果未指定）
        if character is None:
            character = self.get_random_character()

        # 从词汇库获取具体词汇
        features = self.vocabulary.get("身体部位", []) + self.vocabulary.get(
            "服装与装扮", []
        )
        actions = self.vocabulary.get("动作与感觉", [])
        results = self.vocabulary.get("高潮与射精", [])
        states = self.vocabulary.get("状态与反应", [])
        descriptive_adjectives = self.vocabulary.get("描述性形容词", [])
        time_references = self.vocabulary.get("时间与情境", [])

        # 构建标题 - 更多变化
        patterns = [
            # 模式1: 角色+特征+我直接+动作+结果
            lambda: f"{character} {random.choice(features) if features else '黑丝'} 我直接 {random.choice(actions) if actions else '社保'} {random.choice(results) if results else '喷脸'}",
            # 模式2: 角色+特征+动作+我+身体部位+感觉
            lambda: f"{character} {random.choice(features) if features else '白虎穴'} {random.choice(actions) if actions else '坐我嘴'} 我 {random.choice(self.vocabulary.get('身体部位', ['舌头', '鸡巴', '脸'])) if self.vocabulary.get('身体部位') else random.choice(['舌头', '鸡巴', '脸'])} {random.choice(states) if states else '麻了'}",
            # 模式3: 角色+特征+把+我+动作+结果 (加粗角色名)
            lambda: f"**{character}** {random.choice(features) if features else '臀浪'} 把我 {random.choice(actions) if actions else '夹断'} {random.choice(results) if results else '浓精灌满'}",
            # 模式4: 我+把+角色+特征+动作+结果
            lambda: f"我把{character}的{random.choice(features) if features else '小穴'} {random.choice(actions) if actions else '抽插'} {random.choice(results) if results else '内射'}",
            # 模式5: 角色+特征+太+形容词+让我+动作+结果
            lambda: f"{character}的{random.choice(features) if features else '小穴'} 太{random.choice(descriptive_adjectives) if descriptive_adjectives else '紧'}了 让我{random.choice(actions) if actions else '忍不住'}{random.choice(results) if results else '射了'}",
            # 模式6: 角色+时间+状态/动作+结果
            lambda: f"{character}{random.choice(time_references) if time_references else random.choice(['清晨', '深夜', '下午'])} {random.choice(actions) if actions else '求我'} {random.choice(results) if results else '内射'}",
            # 模式7: 角色+身体部位+被+动作+到+状态 (被动)
            lambda: f"{character}的{random.choice(self.vocabulary.get('身体部位', ['小穴'])) if self.vocabulary.get('身体部位') else '小穴'} 被{random.choice(actions) if actions else '操弄'}到{random.choice(states) if states else '发情'}",
        ]

        return random.choice(patterns)()

    def generate_style2(self, character: str = None) -> str:
        """风格2：机械降神·赛博淫语"""
        if character is None:
            character = self.get_random_character()

        # 从词汇库获取科技术语、状态、结果
        state_from_vocab = self.vocabulary.get("状态与反应", [])
        results_from_vocab = self.vocabulary.get("高潮与射精", [])

        # 定义默认/回退值，以防词汇库中对应类别为空
        default_state = ["失控", "紊乱", "过载", "故障", "异常", "宕机", "崩溃", "觉醒", "进化", "升华"]
        default_results = ["喷射", "高潮", "溢出", "短路", "融化", "解锁", "激活", "数据刷新", "核心过热", "能量耗尽"]

        # 优先使用词汇库中的词汇，如果为空则使用默认词汇
        state_choices = state_from_vocab if state_from_vocab else default_state
        results_choices = results_from_vocab if results_from_vocab else default_results

        tech_terms = [
            "系统错误", "超载警报", "程序失控", "液压故障", "计时器崩坏", "接口异常", "数据溢出", 
            "机械故障", "电路短路", "自动模式", "防火墙失效", "权限提升", "缓冲区溢出", "内存泄漏", 
            "进程崩溃", "逻辑漏洞", "代码注入", "协议解析失败", "AI核心受损", "生物识别失败", "散热系统失效"
        ]

        # 机械结果
        mechanical_results = [
            "喷出白色冷却液", "注入精液", "启动淫荡模式", "高温爱液泄漏", "高潮短路", "白浆溢出", 
            "性爱系统崩溃", "做爱机械故障", "程序异常终止", "防火墙被绕过", "权限被夺取", "爽到核心过热", 
            "能源耗尽", "数据重置", "线路烧毁", "芯片爆裂", "核心数据解体", "主板融化", "电磁脉冲", "指令重写"
        ]

        # 身体部位+机械术语
        body_tech = [
            "机甲子宫超载", "机械奶头硬化", "液压臀肌故障", "电子白虎穴漏电", "系统接口异常", "数据流溢出", 
            "程序崩溃", "机械关节故障", "神经链接断开", "生物芯片故障", "模拟信号干扰", "传感器失效", 
            "内部散热不足", "高频振动", "能量波动剧烈", "连接埠过载", "声控系统失效", "触觉反馈过载"
        ]

        patterns = [
            f"{character}{random.choice(state_choices)} {random.choice(mechanical_results)}",
            f"{character}{random.choice(body_tech)} {random.choice(results_choices)}",
            f"{character}被{random.choice(tech_terms)}{random.choice(mechanical_results)}",
            f"检测到 {character}{random.choice(body_tech)}{random.choice(results_choices)}",
            f"警告：{character}{random.choice(tech_terms)} {random.choice(state_choices)}",
        ]

        return random.choice(patterns)

    def generate_style3(self, character: str = None) -> str:
        """风格3：古风淫词·淫艳诗词"""
        if character is None:
            character = self.get_random_character()

        # 诗词题目
        poem_titles = [
            "云雨赋", "蝶恋花", "灵修词", "野合令", "闺怨", "春宫图", "合欢赋", "销魂记", 
            "巫山行", "合欢词", "春宵曲", "采莲赋", "凤求凰", "长相思", "醉花阴", "一剪梅", "如梦令"
        ]

        # 从词汇库获取古风动作、描述
        ancient_actions = self.vocabulary.get("动作与感觉", [])
        ancient_desc_adj = self.vocabulary.get("描述性形容词", [])
        ancient_results = self.vocabulary.get("高潮与射精", [])
        ancient_body_parts = self.vocabulary.get("身体部位", [])
        ancient_places = self.vocabulary.get("位置与场景", [])
        ancient_times = self.vocabulary.get("时间与情境", [])


        # 补充古风特定词汇
        default_ancient_actions = ["褪霓裳", "舞罢腿开", "跪含龙", "草间卧", "卸钗环", "解罗带", "展玉体", "舒玉体", "露春光", "展纤腰", "移莲步", "舒玉臂", "娇喘", "颤抖"]
        default_ancient_desc = ["白虎穴含露吐芳", "春水泛滥浸檀郎", "玉门开处涌甘泉", "花露滴滴染红妆", "玉体横陈迎君入", "娇喘微微唤郎君", "眉目含情脉脉水", "玉指轻抚桃花源", "芙蓉帐暖度春宵", "红绡帐里展娇躯", "玉臂轻摇引凤来", "樱桃小口含龙吞", "香汗淋漓", "春潮涌动"]
        default_ancient_results = ["玉浆溅我青衫湿", "花露滴滴染红妆", "仙音颤颤绕梁", "湿透鸳鸯枕半边", "一夜销魂君莫问", "春宵一刻值千金", "巫山云雨共缠绵", "娇喘连连夜未央", "红绡帐暖度春宵", "金风玉露一相逢", "便胜却人间无数", "此情可待成追忆", "余韵悠长", "魂飞魄散"]

        # 优先使用词汇库，否则使用默认
        actions_choices = ancient_actions if ancient_actions else default_ancient_actions
        desc_choices = ancient_desc_adj if ancient_desc_adj else default_ancient_desc
        results_choices = ancient_results if ancient_results else default_ancient_results
        body_parts_choices = ancient_body_parts if ancient_body_parts else ["玉门", "花穴", "嫩乳", "香臀"]
        places_choices = ancient_places if ancient_places else ["卧榻", "林间", "花丛", "殿内", "厢房"]
        times_choices = ancient_times if ancient_times else ["月夜", "清晨", "午后", "黄昏"]

        patterns = [
            lambda: f"《{random.choice(poem_titles)}》{character}{random.choice(actions_choices)}，{random.choice(desc_choices)}，{random.choice(results_choices)}",
            lambda: f"{random.choice(times_choices)}，{character}于{random.choice(places_choices)}{random.choice(actions_choices)}，{random.choice(results_choices)}",
            lambda: f"{character} {random.choice(body_parts_choices)}{random.choice(desc_choices)}，引得{random.choice(results_choices)}",
        ]

        return random.choice(patterns)()

    def generate_style4(self, character: str = None) -> str:
        """风格4：街头涂鸦·毒液俚语"""
        if character is None:
            character = self.get_random_character()

        actions = self.vocabulary.get("动作与感觉", [])
        results = self.vocabulary.get("高潮与射精", [])
        body_parts = self.vocabulary.get("身体部位", [])
        states = self.vocabulary.get("状态与反应", [])

        default_comments = ['小穴香香的', '哥哥太猛了', '太骚了 顶不住', '操疯了', '射爆了', '爽死了', '干穿了', '要死了', '求饶了']
        default_dialogs = ['干翻了', '太爽了', '还要', '射了', '爽死了', '不够', '再来', '饶了我', '别停']
        default_verbs = ['爆了', '射了', '喷了', '漏了', '潮了', '湿了', '紧了', '麻了']
        default_actions_short = ['后入', '骑乘', '口交', '颜射', '内射', '肛交', '群交', '轮奸']
        default_time_contexts = ['今天', '昨晚', '刚才', '刚刚']
        default_passive_verbs = ['被操', '被干', '被射', '被灌', '被玩弄', '被开发']

        # 涂鸦风格模式
        patterns = [
            f"**{character}**", # 加粗角色名
            f"{character}~{random.choice(actions) if actions else random.choice(default_comments)}", # 角色~评论
            f"{random.choice(states) if states else random.choice(default_comments)}//{random.choice(results) if results else random.choice(default_dialogs)}", # 状态//对话
            f"**{character}{random.choice(results) if results else random.choice(default_verbs)}**", # 角色+结果动词
            f"{random.choice(actions) if actions else random.choice(default_actions_short)}{character}~{random.choice(results) if results else random.choice(default_comments)}", # 动作+角色~评论
            f"**{random.choice(default_time_contexts)}{character}{random.choice(states) if states else random.choice(default_passive_verbs)}**", # 时间+角色+被动状态/动作
            f"@{character} {random.choice(body_parts) if body_parts else random.choice(['小穴', '批', '大奶'])} {random.choice(default_verbs)}了", # @角色 身体部位 动词了
        ]

        return random.choice(patterns)

    def generate_style5(self, character: str = None) -> str:
        """风格5：深夜电台·喘息ASMR"""
        if character is None:
            character = self.get_random_character()

        # 从词汇库获取词汇
        features = self.vocabulary.get("身体部位", []) + self.vocabulary.get(
            "服装与装扮", []
        )
        actions = self.vocabulary.get("动作与感觉", [])
        results = self.vocabulary.get("高潮与射精", [])
        states = self.vocabulary.get("状态与反应", [])

        # ASMR风格：简短词汇加省略号
        # 确保有足够的词汇选择，否则使用默认
        feature_choices = features if features else ['黑丝', '小穴', '腿心', '臀浪', '奶子']
        action_choices = actions if actions else ['吸入', '夹紧', '榨干', '抽送', '舔弄']
        result_choices = results if results else ['喷出', '高潮', '溢满', '湿透', '颤抖']
        state_choices = states if states else ['娇喘', '呜咽', '酥麻', '失神', '求饶']

        patterns = [
            lambda: f"{character}...{random.choice(feature_choices)}...{random.choice(action_choices)}...{random.choice(result_choices)}",
            lambda: f"{character}...啊...{random.choice(feature_choices)}...嗯...{random.choice(action_choices)}...",
            lambda: f"（喘息）{character}好{random.choice(state_choices)}...要...{random.choice(result_choices)}...",
            lambda: f"（私语）{character}...再...深...一点...（{random.choice(action_choices)}）",
            lambda: f"滴答...滴答...（爱液声）{character}的{random.choice(feature_choices)}...好{random.choice(state_choices)}...",
        ]

        return random.choice(patterns)()

    def generate(
        self, style: int = None, character: str = None, count: int = 1
    ) -> List[str]:
        """生成指定风格的标题，如果风格为None则随机选择（仅当count=1时推荐）"""
        generators = {
            1: self.generate_style1,
            2: self.generate_style2,
            3: self.generate_style3,
            4: self.generate_style4,
            5: self.generate_style5,
        }

        # 如果风格为None，则随机选择一个风格（注意：这个选择对整个count批次生效）
        chosen_style = style if style is not None else random.randint(1, 5)

        if chosen_style not in generators:
            raise ValueError(f"无效的风格编号，可选：{list(generators.keys())}")

        generator_func = generators[chosen_style]
        return [generator_func(character) for _ in range(count)]

    def generate_all_styles(
        self, character: str = None, count: int = 1
    ) -> Dict[int, List[str]]:
        """生成所有风格的标题"""
        return {style: self.generate(style, character, count) for style in range(1, 6)}

    def generate_random_batch(
        self,
        total_count: int,
        random_style: bool = True,
        random_character: bool = True,
        fixed_character_name: str = None, # 新增参数：指定固定的角色名
    ) -> List[str]:
        """
        生成随机批量的标题。
        random_style: True则每个标题随机风格，False则所有标题使用一个随机选定的风格。
        random_character: True则每个标题随机角色，False则所有标题使用一个随机选定的角色。
        fixed_character_name: 如果指定，则使用此角色名，忽略random_character设置。
        """
        titles = []

        # 如果random_character为False，且未指定fixed_character_name，则为整个批次选择一个固定角色
        char_for_batch = None
        if fixed_character_name: # 用户明确指定了固定角色名
            char_for_batch = fixed_character_name
        elif not random_character: # 用户要求固定角色但未指定名字，则随机选择一个作为固定角色
            char_for_
