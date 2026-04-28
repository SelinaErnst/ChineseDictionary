# CJK Radicals Supplement
cjk_rad_supl = "\u2E80-\u2EFF"
# KangXi Radicals
kangxi_rad = "\u2F00-\u2FDF" 
# CJK Strokes
cjk_strokes = "\u31C0-\u31EF"
# CJK Unified Ideographs Extension A
cjk_ext_a = "\u3400-\u4DBF"
# CJK Unified Ideographs
cjk_uni_ideogr = "\u4E00-\u9FFF"


# Extensions B-F
# ext_b_f = "\U00020000-\U0002EBEF"
ext_b_f = "\U00020000-\U0002EBEF"
# Extensions G-J
ext_g_h = "\U00030000-\U0003347F"
ext_i = "\U0002EBF0-\U0002EE5F"

all_ext = f"{ext_b_f}|{ext_g_h}|{ext_i}"

pleco_char = "\ueaaa-\uefff"

chinese_char = f'{cjk_rad_supl}|{kangxi_rad}|{cjk_strokes}|{cjk_ext_a}|{cjk_uni_ideogr}|{all_ext}'
not_chinese_char = f'^{cjk_rad_supl}{kangxi_rad}{cjk_strokes}{cjk_ext_a}{cjk_uni_ideogr}{all_ext}'

PinyinToneMark = {
    0: "aoeiuv\u00fc", 
    1: "\u0101\u014d\u0113\u012b\u016b\u01d6\u01d6", # āōēīūǖǖ
    2: "\u00e1\u00f3\u00e9\u00ed\u00fa\u01d8\u01d8", # áóéíúǘǘ
    3: "\u01ce\u01d2\u011b\u01d0\u01d4\u01da\u01da", # ǎǒěǐǔǚǚ
    4: "\u00e0\u00f2\u00e8\u00ec\u00f9\u01dc\u01dc", # àòèìùǜǜ
}