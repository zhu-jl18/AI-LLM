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
        self.rules_examples = self._load_rules_examples(
            rules_file
        )  # 可以用于未来验证或提示
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
                        # 提取纯中文名作为字典键
                        match = re.match(r"##\s*([\u4e00-\u9fa5]+)", line)
                        if match:
                            current_category = match.group(1).strip()
                        else:
                            # 备用逻辑，尝试获取第一个中文词
                            current_category = (
                                line[3:].split("&")[0].split(" ")[0].strip()
                            )
                            # 如果实在无法匹配中文，回退到原始处理方式（但可能会带英文）
                            if not current_category or not re.match(
                                r"[\u4e00-\u9fa5]+", current_category
                            ):
                                current_category = (
                                    line[3:].split("&")[0].strip()
                                )  # 原始带英文的

                        vocab[current_category] = []
                    elif line.startswith("- ") and current_category:
                        word = line[2:].split(" (")[0].strip()
                        if word:
                            vocab[current_category].append(word)
        except FileNotFoundError:
            print(f"警告: 找不到文件 {file_path}")
            return {}  # 返回空字典
        except Exception as e:
            print(f"加载词汇库时发生错误: {e}")
            return {}
        return vocab

    def _load_rules_examples(self, file_path: str) -> Dict[str, List[Dict]]:
        """加载规则示例（当前未直接用于生成，但可用于参考或未来功能）"""
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
                "远坂凛",
                "saber",
                "亚丝娜",
                "楪祈",
                "御坂美琴",
                "炮姐",
                "时崎狂三",
                "五河琴里",
                "夜刀神十香",
                "四糸乃",
                "八舞耶俱矢",
                "八舞夕弦",
                "诱宵美九",
                "或守鞠亚",
                "园神凛祢",
                "非莉娅",
                "两仪式",
                "浅上藤乃",
                "黑桐鲜花",
                "苍崎青子",
                "久远寺有珠",
                "卡莲",
                "尤菲",
                "C.C.",
                "夏莉",
                "罗伊德",
                "柯内莉娅",
            ],
            "游戏角色": [
                "希尔薇",
                "莫妮卡",
                "星梨花",
                "艾莉卡",
                "千早",
                "亚里沙",
                "真白",
                "伊莉雅",
                "美游",
                "小黑",
                "克洛伊",
                "巴泽特",
                "斯卡哈",
                "斯卡蒂",
                "布伦希尔德",
                "齐格飞",
                "齐格鲁德",
                "源赖光",
                "酒吞童子",
                "茨木童子",
                "玉藻前",
                "清姬",
                "阎魔刀",
            ],
            "原创角色": [
                "苏沐沐",
                "林若曦",
                "慕容雪",
                "欧阳娜娜",
                "上官婉儿",
                "司马嫣然",
                "夏雨荷",
                "魏紫嫣",
                "秦雨瑶",
                "唐婉儿",
                "宋佳音",
                "许清歌",
                "韩雪莉",
                "冯雨晴",
                "邓紫琪",
                "曹颖",
                "萧薰儿",
                "彩鳞",
                "云韵",
                "美杜莎",
                "雅妃",
                "纳兰嫣然",
                "云芝",
                "小医仙",
            ],
            "通用称呼": [
                "学姐",
                "学妹",
                "老师",
                "护士",
                "医生",
                "警察",
                "空姐",
                "女仆",
                "兔女郎",
                "巫女",
                "修女",
                "骑士",
                "法师",
                "牧师",
                "刺客",
                "弓箭手",
                "舞娘",
                "歌姬",
                "偶像",
                "主播",
            ],
            "自定义角色": [],  # 为用户自定义留空
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
                        default_pool[category] = characters  # 添加新分类
        except FileNotFoundError:
            # 如果文件不存在，创建默认的角色池文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_pool, f, ensure_ascii=False, indent=2)
            print(f"已创建默认角色池文件: {file_path}")
        except json.JSONDecodeError:
            print(
                f"警告: 角色池文件 {file_path} 格式错误，将使用默认角色池。请检查文件内容。"
            )
            # 如果JSON文件损坏，也写入默认的
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_pool, f, ensure_ascii=False, indent=2)

        # 确保所有类别至少是一个空列表，避免KeyError
        for category in default_pool:
            if default_pool[category] is None:
                default_pool[category] = []

        return default_pool

    def get_random_character(self) -> str:
        """从角色池中随机选择一个角色"""
        # 随机选择一个类别，确保类别非空
        available_categories = [
            cat for cat, chars in self.character_pool.items() if chars
        ]
        if not available_categories:
            return "某人"  # Fallback if no characters available

        category = random.choice(available_categories)
        # 从该类别中随机选择一个角色
        return random.choice(self.character_pool[category])

    def get_random_word(self, category: str, fallback_list: List[str] = None) -> str:
        """从指定类别获取随机词汇，并支持回退列表"""
        if fallback_list is None:
            fallback_list = []  # 默认空列表，防止NoneType错误

        if category in self.vocabulary and self.vocabulary[category]:
            return random.choice(self.vocabulary[category])
        elif fallback_list:
            return random.choice(fallback_list)
        return "未知词汇"  # 最终回退

    def generate_style1(self, character: str = None) -> str:
        """风格1：神经刀第一人称 - 更加多样化，贴近rules.md示例"""
        if character is None:
            character = self.get_random_character()

        # 从词汇库获取词汇，提供精简回退列表
        # 身体部位和服装与装扮合并为features
        features = self.vocabulary.get("身体部位", []) + self.vocabulary.get(
            "服装与装扮", []
        )
        features_fallback = ["小穴", "批", "臀浪", "黑丝", "白虎穴", "腿间"]

        actions = self.vocabulary.get("动作与感觉", [])
        actions_fallback = ["操", "社保", "夹断", "坐我嘴", "吸", "榨", "开闸", "掰开"]

        results = self.vocabulary.get("高潮与射精", [])
        results_fallback = [
            "喷脸",
            "喷汁",
            "浓精灌满",
            "射了三次",
            "内射",
            "白浆",
            "射我满屏",
        ]

        states = self.vocabulary.get("状态与反应", [])
        states_fallback = ["麻了", "硬了", "疯了", "叫床", "高潮"]

        descriptive_adjectives = self.vocabulary.get("描述性形容词", [])
        adj_fallback = ["紧", "骚", "淫荡", "湿"]

        times = self.vocabulary.get("时间与情境", [])
        times_fallback = ["清晨", "深夜", "下午", "这时间", "计时器响了"]

        # 额外的俚语/特殊词汇，不在主要分类中但用于特定风格
        slang_words = ["鸡巴", "奶子", "鸭嘴", "USB接口", "榨汁机"]
        dialogue_starters = ["说", "问"]
        dialogue_parts = [
            "裙子颜色是我鸡巴染的",
            "要含着我鸡巴吸",
            "吸到魔力变奶白色了",
            "补魔要含着我鸡巴",
        ]
        concept_words = ["骑舞", "骑乘", "补魔", "鸭子坐合集"]

        patterns = [
            # 模式1: 角色+特征+我直接+动作+结果 (如: 凛酱黑丝JK我直接社保腿间开闸白浆喷我脸上了)
            lambda: f"{character}{self.get_random_word('服装与装扮', ['黑丝', 'JK'])}{self.get_random_word('身体部位', features_fallback)}我直接{self.get_random_word('动作与感觉', actions_fallback)}{self.get_random_word('身体部位', features_fallback)}{self.get_random_word('动作与感觉', ['开闸'])}{self.get_random_word('高潮与射精', results_fallback)}",
            # 模式2: 角色+身体部位+动作+我+身体部位+状态 (如: 妖刀姬白虎穴坐我嘴滴汁操我舌头麻了)
            lambda: f"{character}{self.get_random_word('身体部位', ['白虎穴', '小穴'])}{self.get_random_word('动作与感觉', ['坐我嘴'])}{self.get_random_word('高潮与射精', ['滴汁'])}{self.get_random_word('动作与感觉', ['操我'])}{self.get_random_word('身体部位', ['舌头', '脸', '鸡巴'])} {self.get_random_word('状态与反应', states_fallback)}了",
            # 模式3: 角色+动作+身体部位+甩我嘴里+结果 (如: 白毛狐狸精坐上来自己动奶子甩我嘴里射了三次)
            lambda: f"{character}{self.get_random_word('动作与感觉', ['坐上来自己动'])}{self.get_random_word('身体部位', ['奶子', '大奶'])}甩我嘴里{self.get_random_word('高潮与射精', results_fallback)}",
            # 模式4: 角色+特征+把我+动作+结果+动作 (如: 唐姐臀浪把我鸡巴夹断了浓精灌满她还在上面摇)
            lambda: f"{character}{self.get_random_word('身体部位', features_fallback)}把我{self.get_random_word('动作与感觉', actions_fallback)}{self.get_random_word('高潮与射精', results_fallback)}她还在上面{self.get_random_word('动作与感觉', ['摇', '颤动'])}",
            # 模式5: 我把+角色+的+身体部位+动作+结果 (如: 我把C.C.的小穴抽插内射)
            lambda: f"我把{character}的{self.get_random_word('身体部位', ['小穴', '蜜穴', '花穴'])}{self.get_random_word('动作与感觉', ['抽插', '猛干', '深插', '干穿'])}{self.get_random_word('高潮与射精', ['内射', '射爆', '射满'])}",
            # 模式6: 角色+的+身体部位+太+形容词+了+让我+动作+结果 (如: 角色的小穴太紧了让我忍不住射了)
            lambda: f"{character}的{self.get_random_word('身体部位', ['小穴', '蜜穴', '批'])}太{self.get_random_word('描述性形容词', adj_fallback)}了让我{self.get_random_word('动作与感觉', ['忍不住', '不得不'])}{self.get_random_word('高潮与射精', ['射了', '喷了', '射爆'])}",
            # 模式7: 角色+时间+状态+动作 (如: 萧薰儿清晨求我内射)
            lambda: f"{character}{self.get_random_word('时间与情境', times_fallback)}{self.get_random_word('状态与反应', ['求干', '求饶', '发情'])}{self.get_random_word('动作与感觉', actions_fallback)}",
            # 模式8: 角色+身体部位+被+动作+到+状态 (如: 角色的小穴被操弄到发情)
            lambda: f"{character}的{self.get_random_word('身体部位', ['小穴', '蜜穴', '批'])}被{self.get_random_word('动作与感觉', ['操弄', '猛干', '蹂躏'])}到{self.get_random_word('状态与反应', ['发情', '求饶', '高潮', '失禁'])}",
            # 模式9: 概念+我把她们+身体部位+掰成+比喻+动作 (如: 鸭子坐合集？是我把她们屁股掰成鸭嘴操合集)
            lambda: f"{random.choice(concept_words)}？是我把她们{self.get_random_word('身体部位', ['屁股'])}掰成{random.choice(slang_words)}{self.get_random_word('动作与感觉', ['操合集', '猛干'])}",
            # 模式10: 服装+掀起来直接+动作+对话 (如: 红色连衣裙掀起来直接开干妹妹说裙子颜色是我鸡巴染的)
            lambda: f"{self.get_random_word('服装与装扮', ['连衣裙', '短裙', 'JK裙'])}掀起来直接{self.get_random_word('动作与感觉', ['开干', '猛操'])}{random.choice(dialogue_starters)}{character}{random.choice(dialogue_parts)}",
        ]

        return random.choice(patterns)()

    def generate_style2(self, character: str = None) -> str:
        """风格2：机械降神·赛博淫语 - 更多科技感，贴近rules.md示例"""
        if character is None:
            character = self.get_random_character()

        # 从词汇库获取词汇，提供精简回退列表
        states = self.vocabulary.get("状态与反应", [])
        states_fallback = [
            "失控",
            "紊乱",
            "过载",
            "故障",
            "异常",
            "宕机",
            "崩溃",
            "觉醒",
            "进化",
            "升华",
        ]

        results = self.vocabulary.get("高潮与射精", [])
        results_fallback = [
            "喷射",
            "高潮",
            "溢出",
            "短路",
            "融化",
            "解锁",
            "激活",
            "数据刷新",
            "核心过热",
            "能量耗尽",
        ]

        # 机械/赛博特有词汇，这些词汇可能不适合放入通用词汇库，因此在此处提供回退或硬编码列表
        tech_terms = [
            "系统错误",
            "超载警报",
            "程序失控",
            "液压故障",
            "计时器崩坏",
            "接口异常",
            "数据溢出",
            "机械故障",
            "电路短路",
            "自动模式",
            "防火墙失效",
            "权限提升",
            "缓冲区溢出",
            "内存泄漏",
            "进程崩溃",
            "逻辑漏洞",
            "代码注入",
            "协议解析失败",
            "AI核心受损",
            "生物识别失败",
            "散热系统失效",
            "能量核心",
            "传感过载",
        ]

        mechanical_results = [
            "喷出白色冷却液",
            "注入精液",
            "启动淫荡模式",
            "高温爱液泄漏",
            "高潮短路",
            "白浆溢出",
            "性爱系统崩溃",
            "做爱机械故障",
            "程序异常终止",
            "防火墙被绕过",
            "权限被夺取",
            "爽到核心过热",
            "能源耗尽",
            "数据重置",
            "线路烧毁",
            "芯片爆裂",
            "核心数据解体",
            "主板融化",
            "电磁脉冲",
            "指令重写",
            "全身痉挛",
        ]

        body_tech = [
            "机甲子宫",
            "机械奶头",
            "液压臀肌",
            "电子白虎穴",
            "系统接口",
            "神经链接",
            "生物芯片",
            "内部散热器",
            "核心引擎",
            "敏感传感器",
        ]

        actions_tech = [
            "注入病毒代码",
            "当USB接口狂插",
            "吸我鸡巴像榨汁机",
            "后入",
            "骑乘模式",
        ]
        time_references_tech = ["这时间标记是叫床时长？", "5分40秒", "计时器响了"]

        patterns = [
            # 模式1: 科技身体部位+状态+角色+身体部位+动作+科技液体 (如: 机甲子宫超载警报梵蒂白虎穴喷出白色冷却液)
            lambda: f"{random.choice(body_tech)}{self.get_random_word('状态与反应', states_fallback)}{random.choice(['警报'])} {character}{self.get_random_word('身体部位', ['白虎穴', '小穴'])}{self.get_random_word('动作与感觉', ['喷出', '溢出'])}{random.choice(mechanical_results)}",
            # 模式2: 角色+服装/装备+系统错误+被动动作+科技物质+结果 (如: 凛酱黑丝JK系统错误被我注入病毒代码后喷汁)
            lambda: f"{character}{self.get_random_word('服装与装扮', ['黑丝', 'JK', '机甲'])}{random.choice(tech_terms)}被我{random.choice(['注入病毒代码', '物理连接'])}{random.choice(['后喷汁', '数据溢出', '系统崩溃'])}",
            # 模式3: 角色+程序状态+模式+第一人称动作+身体部位+比喻+动作 (如: 小舞程序失控骑乘模式把我鸡巴当USB接口狂插)
            lambda: f"{character}{random.choice(tech_terms)}{random.choice(['骑乘模式', '全自动模式', '自动模式'])}把我{self.get_random_word('身体部位', ['鸡巴', '身体'])}{random.choice(['当USB接口狂插', '当榨汁机', '吸我鸡巴像榨汁机'])}",
            # 模式4: 角色+计时器状态+身体部位+漏电+时间+结果 (如: 云曦计时器崩坏白虎穴漏电5分40秒射我满屏)
            lambda: f"{character}{random.choice(tech_terms)}{self.get_random_word('身体部位', ['白虎穴', '身体'])}漏电{random.choice(time_references_tech)}{self.get_random_word('高潮与射精', results_fallback)}",
            # 模式5: 角色+科技身体部位+故障+身体部位+动作+科技液体 (如: 唐姐臀肌液压故障白虎穴喷出高温润滑液)
            lambda: f"{character}{random.choice(body_tech)}{random.choice(tech_terms)}{self.get_random_word('身体部位', ['白虎穴', '小穴'])}{self.get_random_word('动作与感觉', ['喷出', '溢出'])}{random.choice(mechanical_results)}",
            # 模式6: 检测到+角色+身体科技+结果
            lambda: f"检测到 {character}{random.choice(body_tech)}{random.choice(results_fallback)}",
            # 模式7: 警告：角色+系统状态+后果
            lambda: f"警告：{character}{random.choice(tech_terms)} {self.get_random_word('状态与反应', states_fallback)}",
        ]

        return random.choice(patterns)()

    def generate_style3(self, character: str = None) -> str:
        """风格3：古风淫词·淫艳诗词 - 更多古典美，贴近rules.md示例"""
        if character is None:
            character = self.get_random_character()

        # 诗词题目
        poem_titles = [
            "云雨赋",
            "蝶恋花",
            "灵修词",
            "野合令",
            "闺怨",
            "春宫图",
            "合欢赋",
            "销魂记",
            "巫山行",
            "合欢词",
            "春宵曲",
            "采莲赋",
            "凤求凰",
            "长相思",
            "醉花阴",
            "一剪梅",
            "如梦令",
            "西江月",
            "虞美人",
        ]

        # 从词汇库获取古风动作、描述、结果
        actions = self.vocabulary.get("动作与感觉", [])
        actions_fallback = [
            "褪霓裳",
            "舞罢腿开张",
            "跪含龙",
            "草间卧",
            "卸钗环",
            "解罗带",
            "展玉体",
            "舒玉体",
            "露春光",
            "展纤腰",
            "移莲步",
            "舒玉臂",
            "娇喘",
            "颤抖",
            "吸尽元阳",
        ]

        descriptive_adjectives = self.vocabulary.get("描述性形容词", [])
        desc_fallback = [
            "含露吐芳",
            "春水泛滥",
            "玉门开处涌甘泉",
            "花露滴滴染红妆",
            "玉体横陈迎君入",
            "娇喘微微唤郎君",
            "眉目含情脉脉水",
            "玉指轻抚桃花源",
            "芙蓉帐暖",
            "红绡帐里展娇躯",
            "玉臂轻摇引凤来",
            "樱桃小口含龙吞",
            "香汗淋漓",
            "春潮涌动",
            "淫香浮",
        ]

        results = self.vocabulary.get("高潮与射精", [])
        results_fallback = [
            "玉浆溅我青衫湿",
            "仙音颤颤绕梁",
            "湿透鸳鸯枕半边",
            "一夜销魂君莫问",
            "春宵一刻值千金",
            "巫山云雨共缠绵",
            "娇喘连连夜未央",
            "红绡帐暖度春宵",
            "金风玉露一相逢",
            "便胜却人间无数",
            "此情可待成追忆",
            "余韵悠长",
            "魂飞魄散",
            "化乳浆",
        ]

        body_parts = self.vocabulary.get("身体部位", [])
        body_parts_fallback = ["白虎穴", "玉门", "花穴", "嫩乳", "香臀", "小穴"]

        places = self.vocabulary.get("位置与场景", [])
        places_fallback = ["卧榻", "林间", "花丛", "殿内", "厢房", "闺房", "草间"]

        times = self.vocabulary.get("时间与情境", [])
        times_fallback = ["月夜", "清晨", "午后", "黄昏", "春宵"]

        patterns = [
            # 模式1: 《诗词名》角色动作，描述，结果 (如: 《云雨赋》仙子褪霓裳，白虎穴含露吐芳，玉浆溅我青衫湿)
            lambda: f"《{random.choice(poem_titles)}》{character}{self.get_random_word('动作与感觉', actions_fallback)}，{self.get_random_word('描述性形容词', desc_fallback)}，{self.get_random_word('高潮与射精', results_fallback)}",
            # 模式2: 《诗词名》角色动作1，动作2+描述，结果 (如: 《灵修词》灵儿跪含龙，吸尽元阳化乳浆，仙音颤颤绕梁)
            lambda: f"《{random.choice(poem_titles)}》{character}{self.get_random_word('动作与感觉', actions_fallback)}，{self.get_random_word('动作与感觉', actions_fallback)}{self.get_random_word('高潮与射精', results_fallback)}，{self.get_random_word('状态与反应', ['仙音颤颤'])}",
            # 模式3: 时间，角色于地点动作，结果 (如: 小医仙草间卧，白虎穴吞杵杵，药香混着淫香浮)
            lambda: f"{self.get_random_word('时间与情境', times_fallback)}，{character}于{self.get_random_word('位置与场景', places_fallback)}{self.get_random_word('动作与感觉', actions_fallback)}，{self.get_random_word('身体部位', body_parts_fallback)}{self.get_random_word('动作与感觉', ['吞杵杵'])}，{self.get_random_word('描述性形容词', ['药香混着淫香浮'])}",
            # 模式4: 角色+身体部位+描述，引得结果
            lambda: f"{character}{self.get_random_word('身体部位', body_parts_fallback)}{self.get_random_word('描述性形容词', desc_fallback)}，引得{self.get_random_word('高潮与射精', results_fallback)}",
            # 模式5: 角色+动作+身体部位+描述+结果 (如: 曹颖卸钗环，玉门开处涌甘泉，湿透鸳鸯枕半边)
            lambda: f"{character}{self.get_random_word('动作与感觉', actions_fallback)}，{self.get_random_word('身体部位', body_parts_fallback)}{self.get_random_word('描述性形容词', desc_fallback)}，{self.get_random_word('高潮与射精', results_fallback)}",
        ]

        return random.choice(patterns)()

    def generate_style4(self, character: str = None) -> str:
        """风格4：街头涂鸦·毒液俚语 - 粗犷直接，贴近rules.md示例"""
        if character is None:
            character = self.get_random_character()

        actions = self.vocabulary.get("动作与感觉", [])
        actions_fallback = ["操", "干", "射", "掰", "插", "顶"]

        results = self.vocabulary.get("高潮与射精", [])
        results_fallback = [
            "爆了",
            "射了",
            "喷了",
            "漏了",
            "潮了",
            "湿了",
            "紧了",
            "麻了",
            "操穿",
            "干翻",
            "射满",
            "喷屏",
        ]

        body_parts = self.vocabulary.get("身体部位", [])
        body_parts_fallback = ["小穴", "批", "大奶", "屁股", "嘴", "鸡巴"]

        states = self.vocabulary.get("状态与反应", [])
        states_fallback = [
            "太骚了",
            "顶不住",
            "操疯了",
            "爽死了",
            "要死了",
            "求饶了",
            "发情了",
        ]

        # 俚语/口语评论
        comments = self.vocabulary.get("描述性形容词", []) + [
            "小穴香香的",
            "哥哥太猛了",
            "太骚了 顶不住",
            "操疯了",
            "射爆了",
            "爽死了",
            "干穿了",
            "不够",
            "还要",
        ]
        comments_fallback = [
            "小穴香香的",
            "哥哥太猛了",
            "太骚了 顶不住",
            "操疯了",
            "射爆了",
            "爽死了",
            "干穿了",
            "要死了",
            "求饶了",
        ]

        # 对话或补充说明
        dialogs = [
            "妹妹说裙子颜色是我鸡巴染的",
            "这时间标记是叫床时长？",
            "我射她嘴里计时器响了",
            "操穿",
            "干翻",
            "射满",
            "喷屏",
        ]

        time_contexts = self.vocabulary.get("时间与情境", [])
        time_contexts_fallback = ["今天", "昨晚", "刚才", "刚刚"]

        passive_verbs = ["被操", "被干", "被射", "被灌", "被玩弄", "被开发", "被捅穿"]

        patterns = [
            # 模式1: **角色** (如: **白毛狐狸精**)
            lambda: f"**{character}**",
            # 模式2: 概念~评论 (如: 鸭子坐合集~我把她们屁股掰成鸭嘴操穿)
            lambda: f"{random.choice(['鸭子坐合集', '后入合集', '丝袜合集'])}~我把她们{self.get_random_word('身体部位', ['屁股', '小穴'])}掰成{random.choice(['鸭嘴', '两半'])}{self.get_random_word('动作与感觉', ['操穿', '干爆'])}",
            # 模式3: 动作+服装+直接干//对话 (如: 红色连衣裙掀起来直接开干妹妹说裙子颜色是我鸡巴染的)
            lambda: f"{self.get_random_word('服装与装扮', ['红裙', '连衣裙'])}掀起来直接{self.get_random_word('动作与感觉', ['开干', '猛干'])}//{random.choice(dialogs)}",
            # 模式4: **角色+时间+描述** (如: **云曦计时叫床5分40秒**)
            lambda: f"**{character}{self.get_random_word('时间与情境', time_contexts_fallback)}{self.get_random_word('状态与反应', states_fallback)}{random.choice(['计时叫床5分40秒', '被操了一整晚'])}**",
            # 模式5: 角色+身体部位+动作+身体部位+状态 (如: 妖刀姬白虎穴坐我嘴滴汁操我舌头麻了 - 虽然重复，但此风格也接受直白表达)
            lambda: f"{character}{self.get_random_word('身体部位', ['白虎穴', '小穴'])}{self.get_random_word('动作与感觉', ['坐我嘴'])}{self.get_random_word('高潮与射精', ['滴汁'])}{self.get_random_word('动作与感觉', ['操我'])}{self.get_random_word('身体部位', ['舌头', '脸', '鸡巴'])} {self.get_random_word('状态与反应', states_fallback)}了",
            # 模式6: 角色~评论
            lambda: f"{character}~{self.get_random_word('描述性形容词', comments_fallback)}",
            # 模式7: 动词+角色~评论
            lambda: f"{self.get_random_word('动作与感觉', actions_fallback)}{character}~{self.get_random_word('描述性形容词', comments_fallback)}",
            # 模式8: @角色 身体部位 动词了
            lambda: f"@{character} {self.get_random_word('身体部位', body_parts_fallback)} {self.get_random_word('高潮与射精', results_fallback)}了",
            # 模式9: **时间+角色+被动动词**
            lambda: f"**{random.choice(time_contexts_fallback)}{character}{random.choice(passive_verbs)}**",
        ]

        return random.choice(patterns)()

    def generate_style5(self, character: str = None) -> str:
        """风格5：深夜电台·喘息ASMR - 破碎、模糊、强调听觉，贴近rules.md示例"""
        if character is None:
            character = self.get_random_character()

        # 从词汇库获取词汇，提供精简回退列表
        features = self.vocabulary.get("身体部位", []) + self.vocabulary.get(
            "服装与装扮", []
        )
        features_fallback = ["黑丝", "小穴", "腿开", "臀浪", "奶子", "腿心", "玉门"]

        actions = self.vocabulary.get("动作与感觉", [])
        actions_fallback = ["吸", "榨", "夹", "灌", "抽插", "舔弄", "研磨"]

        results = self.vocabulary.get("高潮与射精", [])
        results_fallback = [
            "喷屏",
            "爆",
            "顶",
            "麻了",
            "白浆",
            "高潮",
            "溢出",
            "湿透",
            "颤抖",
        ]

        states = self.vocabulary.get("状态与反应", [])
        states_fallback = ["娇喘", "呜咽", "酥麻", "失神", "求饶", "发骚", "呻吟"]

        # ASMR特有语气词、声音描述
        onomatopoeia = ["嗯...", "啊...", "哈啊...", "哼...", "呜...", "滴答...滴答..."]
        sound_descriptions = [
            "（喘息）",
            "（私语）",
            "（爱液声）",
            "（淫水声）",
            "（撞击声）",
            "（肉体摩擦声）",
        ]
        sensations = [
            "好紧...",
            "好湿...",
            "好热...",
            "好深...",
            "好满...",
            "好涨...",
            "好舒服...",
        ]

        patterns = [
            # 模式1: 角色...特征...动作...结果 (如: 凛酱...黑丝...腿开...白浆...喷屏)
            lambda: f"{character}...{self.get_random_word('身体部位', features_fallback)}...{self.get_random_word('动作与感觉', actions_fallback)}...{self.get_random_word('高潮与射精', results_fallback)}",
            # 模式2: 角色...语气词...特征...语气词...动作... (如: 小舞...啊...小穴...嗯...吸...)
            lambda: f"{character}...{random.choice(onomatopoeia)}{self.get_random_word('身体部位', features_fallback)}...{random.choice(onomatopoeia)}{self.get_random_word('动作与感觉', actions_fallback)}...",
            # 模式3: (声音描述)角色好状态...要...结果... (如: （喘息）角色好酥麻...要...高潮...)
            lambda: f"{random.choice(sound_descriptions)}{character}好{self.get_random_word('状态与反应', states_fallback)}...要...{self.get_random_word('高潮与射精', results_fallback)}...",
            # 模式4: (私语)角色...程度...方向...（动作） (如: （私语）角色...再...深...一点...（抽插）)
            lambda: f"（私语）{character}...再...{random.choice(['深', '快', '用力'])}...一点...（{self.get_random_word('动作与感觉', actions_fallback)}）",
            # 模式5: 滴答...滴答...（声音）角色的特征...好状态... (如: 滴答...滴答...（爱液声）角色的腿心...好湿...)
            lambda: f"{random.choice(onomatopoeia)}{random.choice(sound_descriptions)}{character}的{self.get_random_word('身体部位', features_fallback)}...好{self.get_random_word('状态与反应', states_fallback)}...",
            # 模式6: 角色...动作...状态...结果... (如: 灵儿...含...吸...魔力...奶白...操 - 简化和 ASMR 化)
            lambda: f"{character}...{self.get_random_word('动作与感觉', ['含', '吸', '吞'])}...{self.get_random_word('高潮与射精', ['魔力', '奶白'])}...{self.get_random_word('动作与感觉', ['操', '弄'])}...",
            # 模式7: 角色...全自动...身体部位...动作...比喻...结果... (如: 小舞...全自动...小穴...吸...榨汁...爆)
            lambda: f"{character}...全自动...{self.get_random_word('身体部位', ['小穴', '蜜穴'])}...{self.get_random_word('动作与感觉', actions_fallback)}...{random.choice(['榨汁', '狂吸'])}...{self.get_random_word('高潮与射精', results_fallback)}...",
            # 模式8: 角色...特征...动作...结果...（附加状态）
            lambda: f"{character}...{self.get_random_word('身体部位', features_fallback)}...{self.get_random_word('动作与感觉', actions_fallback)}...{self.get_random_word('高潮与射精', results_fallback)}...（{self.get_random_word('状态与反应', states_fallback)}）",
        ]

        return random.choice(patterns)()

    def generate_style6(self, character: str = None) -> str:
        """风格6：新闻报道式 / 调查报告式"""
        if character is None:
            character = self.get_random_character()

        # 核心词汇
        body_parts = self.get_random_word("身体部位", ["私处", "小穴", "乳房", "臀部"])
        actions = self.get_random_word(
            "动作与感觉", ["淫乱", "暴露", "性行为", "高潮", "滥交"]
        )
        states = self.get_random_word("状态与反应", ["失控", "异常", "发情", "沉沦"])
        results = self.get_random_word("高潮与射精", ["精液", "淫水", "潮吹"])
        time_context = self.get_random_word("时间与情境", ["深夜", "秘密", "私下"])
        location = self.get_random_word(
            "位置与场景", ["酒店", "地下室", "废弃工厂", "公共场所"]
        )
        adjectives = self.get_random_word(
            "描述性形容词", ["惊人", "深度", "独家", "震惊", "异常"]
        )

        # 报道常用语
        report_terms = [
            "【独家揭秘】",
            "【深度报告】",
            "【紧急曝光】",
            "最新调查显示：",
            "内部人士透露：",
            "重磅新闻！",
        ]
        verbs_report = ["曝光", "揭露", "发现", "披露", "证实", "捕捉到"]
        reactions = ["引发轩然大波", "令人震惊", "社会哗然", "引发争议", "触目惊心"]
        data_terms = ["数据显示", "报告指出", "据统计", "分析表明"]
        status_terms = ["私生活", "身体状态", "秘密档案", "行为模式"]

        patterns = [
            # 模式1: 【独家揭秘】角色名 身体部位 惊人内幕曝光，数据显示...
            lambda: f"{random.choice(report_terms)}{character} {body_parts} {adjectives}内幕{random.choice(verbs_report)}，{random.choice(data_terms)}其{random.choice(status_terms)}{self.get_random_word('状态与反应', ['令人担忧', '异常频繁', '远超常人'])}",
            # 模式2: 时间 地点 现场报道：角色名 被曝动作，引发社会反响
            lambda: f"{time_context}，{location}现场报道：{character}被曝{actions}，{random.choice(reactions)}",
            # 模式3: 深度报告：角色名 私生活紊乱，研究发现其特征存在异常状态
            lambda: f"【深度报告】{character}{random.choice(status_terms)}{self.get_random_word('状态与反应', ['紊乱', '糜烂'])}，研究发现其{self.get_random_word('身体部位', ['生理机制', '性激素'])}存在{self.get_random_word('状态与反应', states)}",
            # 模式4: 惊人数据：角色名 在情境下动作次数高达数字次
            lambda: f"惊人数据：{character}在{self.get_random_word('时间与情境', ['深夜', '隐秘角落'])}{random.choice(['被', '主动'])}{self.get_random_word('动作与感觉', ['强奸', '侵犯', '做爱'])}次数高达{random.randint(5, 100)}次",
            # 模式5: 专家/研究员 警告：角色名 的身体部位或已不可逆状态
            lambda: f"【权威警示】专家警告：{character}的{body_parts}或已{self.get_random_word('状态与反应', ['不可逆受损', '功能衰竭', '过度开发', '永久性扩张'])}",
            # 模式6: [角色名] 秘密文件流出：揭露其不为人知的一面
            lambda: f"{random.choice(['秘密文件', '内部录像'])}流出：{character}不为人知的{self.get_random_word('状态与反应', ['淫乱', '糜烂'])}内幕{random.choice(['被揭露', '大曝光'])}！",
        ]
        return random.choice(patterns)()

    def generate_style7(self, character: str = None) -> str:
        """风格7：Pornhub 风格"""
        if character is None:
            character = self.get_random_character()

        # 从词汇库获取词汇，并提供精简回退列表
        body_parts = self.get_random_word(
            "身体部位", ["嫩穴", "巨乳", "大屁股", "白虎", "黑丝美腿", "小穴"]
        )
        actions = self.get_random_word(
            "动作与感觉", ["操", "颜射", "内射", "口爆", "强奸", "轮奸", "榨干", "深喉"]
        )
        results = self.get_random_word(
            "高潮与射精", ["潮吹", "白浆喷射", "精液", "高潮", "失禁"]
        )
        descriptive_adj = self.get_random_word(
            "描述性形容词", ["紧致", "湿润", "淫荡", "骚", "绝美"]
        )
        clothing = self.get_random_word(
            "服装与装扮", ["制服", "黑丝", "JK", "比基尼", "女仆装"]
        )
        states = self.get_random_word("状态与反应", ["求饶", "哭喊", "发情", "被迫"])
        locations = self.get_random_word(
            "位置与场景", ["办公室", "户外", "酒店", "客厅", "浴室"]
        )
        time_context = self.get_random_word("时间与情境", ["第一次", "全程", "深夜"])

        # Pornhub风格特有标签和修饰词
        ph_tags = [
            "POV",
            "Amateur",
            "Cosplay",
            "Big Tits",
            "Anal",
            "Gangbang",
            "Creampie",
            "Cuckold",
            "NTR",
            "Uncensored",
            "HD",
            "Full Video",
            "VR",
        ]
        # qualifiers = ["无码", "高清", "完整版", "独家", "步兵"]
        # durations = [f"{random.randint(5, 45)}分钟", "超长版", "完整收录"]
        intensifiers = ["疯狂", "极致", "高能", "超刺激", "史诗级"]
        preludes = ["[偷拍]", "[直击]", "[震惊]", "[劲爆]"]
        titles = ["小姐姐", "小妹妹", "熟女", "人妻", "邻家女孩"]

        patterns = [
            # 模式1: [标签] 角色+形容词+身体部位+动作+结果 (例: [HD] 远坂凛黑丝巨乳被疯狂颜射潮吹！ )
            lambda: f"[{random.choice(ph_tags)}] {character}{clothing if random.random() < 0.5 else ''}{descriptive_adj}{body_parts}被{random.choice(intensifiers)}{actions}{results}！",
            # 模式2: [标签] 角色+情境+被动动作+状态 (例: [POV] 学生妹小舞课后被老师强奸到失禁)
            lambda: f"[{random.choice(ph_tags)}] {self.get_random_word('通用称呼', titles)}{character}{self.get_random_word('时间与情境', ['课后', '放学后', '深夜'])}{random.choice(['被老师', '被陌生人'])}{self.get_random_word('动作与感觉', ['强奸', '猛操', '轮奸'])}到{states}",
            # 模式3: [地点] 角色+特定行为+时长/画质 (例: [办公室] 人妻唐紫尘被同事无码内射，高清完整版)
            lambda: f"[{locations}] {character}{self.get_random_word('动作与感觉', ['被灌满', '被内射'])}，",
            # 模式4: [NTR/COS] 角色+形容词+身体部位+被+动作+结果+完整度 (例: [NTR] 纯情小医仙嫩穴被路人操到高潮，高清完整版)
            lambda: f"[{random.choice(['NTR', 'COS'])}] {self.get_random_word('描述性形容词', ['纯情', '清纯'])}{character}{body_parts}被{random.choice(['路人', '狗', '触手'])}{actions}到{results}，",
            # 模式5: [偷拍/独家] 角色+行为+现场/后果 (例: [独家] 赵灵儿补魔仪式全程潮吹喷水，震惊)
            lambda: f"{random.choice(preludes)}{character}{time_context}{self.get_random_word('动作与感觉', ['做爱', '补魔', '骑乘'])}仪式{random.choice(['全程', '现场'])} {self.get_random_word('高潮与射精', ['潮吹喷水', '大喷特喷'])}，{self.get_random_word('描述性形容词', ['震惊', '惊人'])}",
            # 模式6: 角色+服装+核心动作+状态，时长 (例: 荷光者梵蒂机甲下黑丝榨汁机高潮痉挛，10分钟)
            lambda: f"{character}{clothing if random.random() < 0.7 else ''}{self.get_random_word('动作与感觉', ['深喉', '榨汁', '狂操'])}到{states}",
            # 模式7: 角色+主题+（身体部位/动作/结果） (例: 云曦时间标记是叫床时长？我射她嘴里计时器响了)
            lambda: f"{character}{random.choice(['计时器', '时间标记'])}是{random.choice(['叫床', '淫叫'])}时长？我{self.get_random_word('动作与感觉', ['射她嘴里', '灌她满嘴'])}计时器响了",
            # 模式8: [角色扮演] 角色+场景+动作+结果 (例: [女仆] 远坂凛女仆装在我面前黑丝露出，被我操到哭着求饶)
            lambda: f"[{self.get_random_word('服装与装扮', ['女仆', '护士', '兔女郎'])}]{character}{self.get_random_word('位置与场景', ['家里', '卧室', '浴室'])}，被我{self.get_random_word('动作与感觉', ['猛干', '操翻'])}到{states}",
            # 模式9: 角色+形容词+身体部位+动作 (例: 白毛狐狸精骚穴坐脸狂喷汁)
            lambda: f"{character}{descriptive_adj}{body_parts}{self.get_random_word('动作与感觉', ['坐脸', '口含', '坐嘴'])} {self.get_random_word('高潮与射精', ['狂喷汁', '滴汁'])}",
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
            6: self.generate_style6,  # 新增
            7: self.generate_style7,  # 新增
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
        fixed_character_name: str = None,  # 新增参数：指定固定的角色名
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
        if fixed_character_name:  # 用户明确指定了固定角色名
            char_for_batch = fixed_character_name
        elif (
            not random_character
        ):  # 用户要求固定角色但未指定名字，则随机选择一个作为固定角色
            char_for_batch = self.get_random_character()

        # 如果random_style为False，则为整个批次选择一个固定风格
        style_for_batch = None
        if not random_style:
            style_for_batch = random.randint(1, 5)

        for _ in range(total_count):
            # 确定当前标题的风格
            current_style = random.randint(1, 5) if random_style else style_for_batch

            # 确定当前标题的角色
            current_character = char_for_batch
            if (
                random_character and not fixed_character_name
            ):  # 只有当允许随机角色且没有指定固定角色名时，才每次随机
                current_character = self.get_random_character()

            # 生成一个标题，这里的count固定为1
            title = self.generate(current_style, current_character, 1)[0]
            titles.append(title)

        return titles

    def add_character(self, category: str, character: str):
        """添加新角色到池子"""
        # 如果分类不存在，则创建它
        if category not in self.character_pool:
            self.character_pool[category] = []

        # 检查角色是否已存在，避免重复添加
        if character not in self.character_pool[category]:
            self.character_pool[category].append(character)
            print(f"已添加角色 '{character}' 到分类 '{category}'")
            self._save_character_pool()
        else:
            print(f"角色 '{character}' 已存在于分类 '{category}' 中，无需重复添加。")

    def _save_character_pool(self, file_path: str = "characters.json"):
        """保存角色池到文件"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.character_pool, f, ensure_ascii=False, indent=2)

    def show_character_pool(self):
        """显示角色池统计"""
        print("\n=== 角色池统计 ===")
        for category, characters in self.character_pool.items():
            print(f"{category}: {len(characters)} 个角色")
            if len(characters) > 0:
                print(f"  示例: {', '.join(characters[:5])}")


def main():
    parser = argparse.ArgumentParser(description="全自动标题生成器 v4")
    parser.add_argument(
        "-s",
        "--style",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7],  # 更新这里
        help="命名风格 (1-7)，不指定则随机",
    )

    parser.add_argument("-c", "--character", type=str, help="角色名称，不指定则随机")
    parser.add_argument("-n", "--count", type=int, default=1, help="生成数量")
    parser.add_argument(
        "-a", "--all", action="store_true", help="生成所有风格（每个风格生成N个）"
    )
    parser.add_argument("-o", "--output", type=str, help="输出到文件")
    parser.add_argument("--vocab", action="store_true", help="显示词汇库统计")
    parser.add_argument("--chars", action="store_true", help="显示角色池统计")
    parser.add_argument(
        "--add-char",
        type=str,
        nargs=2,
        metavar=("CATEGORY", "NAME"),
        help="添加新角色：--add-char 分类名 角色名",
    )
    parser.add_argument(
        "--batch",
        type=int,
        help="批量生成指定数量的标题，每个标题独立随机风格/角色。默认 random_style=True, random_character=True",
    )
    parser.add_argument(
        "--fixed-style",
        action="store_true",
        help="与--batch连用，使批量生成时所有标题风格固定（随机选定一种）",
    )
    parser.add_argument(
        "--fixed-char",
        action="store_true",
        help="与--batch连用，使批量生成时所有标题角色固定（随机选定一个）",
    )

    args = parser.parse_args()

    # 初始化生成器
    generator = AutoTitleGenerator()

    # --- 特殊功能参数处理 ---
    if args.add_char:
        category, name = args.add_char
        generator.add_character(category, name)
        return

    if args.vocab:
        print("\n=== 词汇库统计 ===")
        for category, words in generator.vocabulary.items():
            print(f"{category}: {len(words)} 个词汇")
            if len(words) > 0:
                print(f"  示例: {', '.join(words[:5])}")
        return

    if args.chars:
        generator.show_character_pool()
        return

    # --- 标题生成逻辑 ---
    titles = []
    style_names = {
        1: "神经刀第一人称",
        2: "机械降神·赛博淫语",
        3: "古风淫词·淫艳诗词",
        4: "街头涂鸦·毒液俚语",
        5: "深夜电台·喘息ASMR",
        6: "新闻报道式 / 调查报告式",  # 新增
        7: "二次元论坛体 / 同人创作标题",  # 新增
    }

    if args.batch:
        # 使用 --batch 模式，提供灵活的随机/固定选项
        titles = generator.generate_random_batch(
            total_count=args.batch,
            random_style=not args.fixed_style,
            random_character=not args.fixed_char
            and args.character is None,  # 只有当没有--fixed-char且没有-c时才随机角色
            fixed_character_name=args.character,  # 如果-c指定了角色，则将其作为固定角色
        )
        print(f"\n=== 批量生成 {args.batch} 个标题 ===")
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")

    elif args.all:
        # 生成所有风格的标题，每个风格生成N个
        results = generator.generate_all_styles(args.character, args.count)
        print("\n=== 所有风格标题 ===")
        for style, style_titles in results.items():
            print(f"\n风格{style} ({style_names[style]}):")
            for i, title in enumerate(style_titles, 1):
                print(f"  {i}. {title}")
        # 将所有标题扁平化以便后续文件输出
        titles = [t for sublist in results.values() for t in sublist]

    else:
        # 默认模式：根据-s和-n参数进行生成
        if args.style is not None:
            # 用户明确指定了风格 (-s X)，生成 N 个该风格的标题
            titles = generator.generate(args.style, args.character, args.count)
            style_name = style_names.get(args.style, f"风格{args.style}")
            print(f"\n=== {style_name} 标题 ===")
            for i, title in enumerate(titles, 1):
                print(f"{i}. {title}")
        else:
            # 用户未指定风格 (-s)，但可能指定了数量 (-n N)。
            # 这符合用户期望的“每个标题独立随机风格”的情况。
            titles = generator.generate_random_batch(
                total_count=args.count,
                random_style=True,  # 每个标题都独立随机选择风格
                random_character=(
                    args.character is None
                ),  # 如果没指定-c，则每个标题角色也随机
                fixed_character_name=args.character,  # 如果-c指定了角色，则用该角色
            )
            print(f"\n=== 随机风格批量标题 ({args.count}个) ===")
            for i, title in enumerate(titles, 1):
                print(f"{i}. {title}")

    # --- 输出到文件 ---
    if args.output and titles:  # 确保有标题才输出
        with open(args.output, "w", encoding="utf-8") as f:
            for title in titles:
                f.write(f"{title}\n")
        print(f"\n结果已保存到: {args.output}")
    elif args.output and not titles:
        print(f"\n没有生成任何标题，因此未保存到文件: {args.output}")


if __name__ == "__main__":
    main()
