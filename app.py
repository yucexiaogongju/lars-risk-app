import streamlit as st
import pandas as pd
import joblib
import sys
import time
import warnings

# 设置网页标题
st.set_page_config(page_title="LARS 风险预测小工具", layout="wide")
st.title("LARS 风险预测小工具")

# 添加用户类型选择
user_type = st.sidebar.radio("请选择您的身份", ["👨‍⚕️ 医护工作者", "👨‍👩‍👧‍👦 患者/家属"])

# 根据用户类型显示不同的介绍
if user_type == "👨‍⚕️ 医护工作者":
    st.markdown("""
    ### 应用介绍
    本工具基于机器学习模型，用于预测直肠癌术后患者发生**低位前切除综合征（LARS）** 的风险。
    模型依据临床常见指标进行快速风险评估，辅助术后管理决策。
    """)
else:
    st.markdown("""
    ### 应用介绍
    您好！本工具旨在帮助您了解直肠癌手术后可能出现的**肠道功能异常（LARS）** 的风险情况。
    请您根据实际情况填写以下信息，我们将为您提供初步的风险评估和建议。
    
    **请注意**：本工具仅供参考，不能替代专业医生的诊断和建议。如有任何健康问题，请及时咨询您的主治医生。
    """)

# 添加进度指示器
progress_bar = st.progress(0)
status_text = st.empty()

# 环境信息
status_text.text("正在检查环境...")
progress_bar.progress(10)
st.subheader("环境信息")
st.write(f"Python 版本: {sys.version.split()[0]}")

try:
    st.write(f"Streamlit 版本: {st.__version__}")
except:
    st.warning("无法获取Streamlit版本")

# 模型加载
status_text.text("正在加载模型...")
progress_bar.progress(30)
st.subheader("模型加载状态")
model_path = 'lars_risk_model.pkl'
model_loaded = False

try:
    with st.spinner("模型加载中，请稍候..."):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = joblib.load(model_path)
    st.success("✅ 模型加载成功！")
    model_loaded = True
    progress_bar.progress(50)
except Exception as e:
    st.error(f"❌ 模型加载失败: {str(e)}")
    st.warning("预测功能将不可用，请检查模型文件是否存在")
    # 显示文件列表
    try:
        import os
        st.write("当前目录文件:", os.listdir('.'))
    except:
        pass

# 输入区域
status_text.text("正在准备输入界面...")
progress_bar.progress(70)
st.sidebar.header("请输入以下特征：")

# 为每个输入项添加说明
if user_type == "👨‍⚕️ 医护工作者":
    st.sidebar.markdown("""
    **指标说明**:
    - 年龄: 患者年龄，年龄越大可能影响术后恢复
    - BMI: 身体质量指数（kg/m²)，反映营养与肥胖状况
    - 肿瘤距离: 肿瘤下缘距肛缘距离，影响手术方式
    - 手术时间: 手术持续时间，时间长可能增加组织创伤
    - 排气天数: 术后首次排气时间，反映肠道功能恢复
    - 肿瘤大小: 肿瘤最大直径或体积（长×宽），影响手术复杂度
    - TNM 分期: 肿瘤临床分期，影响术后恢复与并发症风险（详见下方TNM分期转化说明）
    - 是否新辅助治疗: 术前是否接受放化疗，可能影响肠道功能
    """)
    
    # 添加TNM分期转化说明 - 更新为更专业的表格形式
    with st.sidebar.expander("TNM分期转化说明"):
        st.markdown("""
        ### 结直肠癌简化解剖学分期（基于AJCC第8版TNM系统）
        
        | 分期 | 简明定义（含关键TNM信息） |
        | :--- | :--- |
        | **0期** | 癌细胞位于黏膜最表层，未侵犯深层组织（Tis N0 M0）。 |
        | **I期** | 肿瘤侵犯肠壁肌层以内，无淋巴结和远处转移（T1-2 N0 M0）。 |
        | **II期** | 肿瘤侵犯穿透肠壁肌层至最外层，无淋巴结和远处转移（T3-4 N0 M0）。 |
        | **III期** | 无论肿瘤侵犯深度如何，癌细胞已扩散至区域淋巴结，但无远处转移（任何T N1-2 M0）。 |
        | **IV期** | 无论肿瘤深度或淋巴结情况如何，已发生远处转移（任何T 任何N M1）。 |
        
        **注意**: 此分期被称为"解剖学分期"或"预后分组"，直接根据术后病理报告中的TNM结果进行划分。
        """)
else:
    st.sidebar.markdown("""
    **指标说明**:
    - 年龄: 您的当前年龄
    - BMI: 体重指数，计算公式为：体重(kg) ÷ 身高(m)的平方。例如：体重70kg，身高1.75m，BMI = 70 ÷ (1.75×1.75) = 22.9
    - 肿瘤距离: 肿瘤距离肛门的远近，会影响手术方式
    - 手术时间: 手术进行了多长时间
    - 排气天数: 手术后多久第一次排气，反映肠道开始恢复
    - 肿瘤大小: 肿瘤的体积，通常通过长×宽来计算（单位：厘米）
    - TNM 分期: 医生对肿瘤严重程度的评估（0期=原位癌，I期=早期，II期=中期，III期=局部晚期，IV期=晚期）
    - 是否新辅助治疗: 是否在手术前接受了放疗或化疗，目的是缩小肿瘤，使手术更容易进行
    """)

# 格式化数值显示为两位小数
age = st.sidebar.number_input("年龄 (岁)", min_value=0.0, max_value=120.0, value=50.0, step=1.0, format="%.2f")
BMI = st.sidebar.number_input("BMI (kg/m²)", min_value=10.0, max_value=50.0, value=22.0, step=0.1, format="%.2f")
tumor_dist = st.sidebar.number_input("肿瘤距离 (cm)", min_value=0.0, max_value=50.0, value=5.0, step=0.1, format="%.2f")
surg_time = st.sidebar.number_input("手术时间 (分钟)", min_value=0.0, max_value=600.0, value=180.0, step=1.0, format="%.2f")
exhaust = st.sidebar.number_input("排气天数 (天)", min_value=0.0, max_value=30.0, value=2.0, step=0.5, format="%.2f")
tumor_size = st.sidebar.number_input("肿瘤大小 (cm)", min_value=0.1, max_value=50.0, value=3.0, step=0.1, format="%.2f")

# 对于TNM分期，提供更友好的输入方式
if user_type == "👨‍⚕️ 医护工作者":
    TNM = st.sidebar.number_input("TNM 分期 (数值)", min_value=0.0, max_value=4.0, value=2.0, step=1.0, format="%.2f")
else:
    tnm_options = {"0期 (原位癌)": 0.0, "I期 (早期)": 1.0, "II期 (中期)": 2.0, "III期 (局部晚期)": 3.0, "IV期 (晚期)": 4.0}
    tnm_selected = st.sidebar.selectbox("TNM 分期", options=list(tnm_options.keys()))
    TNM = tnm_options[tnm_selected]

# 对于新辅助治疗，提供更友好的输入方式
if user_type == "👨‍⚕️ 医护工作者":
    neoadjuvant = st.sidebar.number_input("是否新辅助治疗 (0=否, 1=是)", min_value=0.0, max_value=1.0, value=0.0, step=1.0, format="%.2f")
else:
    neoadjuvant_options = {"否": 0.0, "是": 1.0}
    neoadjuvant_selected = st.sidebar.selectbox("是否术前辅助治疗", options=list(neoadjuvant_options.keys()))
    neoadjuvant = neoadjuvant_options[neoadjuvant_selected]

# 预测功能
progress_bar.progress(90)
if model_loaded:
    if st.button("点击预测"):
        try:
            input_data = pd.DataFrame([[age, BMI, tumor_dist, surg_time, exhaust, tumor_size, TNM, neoadjuvant]],
                                     columns=['age', 'BMI', 'tumor_dist', 'surg_time', 'exhaust', 'tumor_size', 'TNM', 'neoadjuvant'])
            
            with st.spinner("预测中..."):
                prediction = model.predict(input_data)[0]
                time.sleep(1)  # 模拟处理时间
            
            # 根据用户类型显示不同的结果解释
            if prediction == 1:
                st.success("✅ 预测结果：存在风险")
                if user_type == "👨‍⚕️ 医护工作者":
                    st.markdown("""
                    **临床建议**: 
                    - 建议加强术后随访，重点关注肠道功能恢复
                    - 考虑康复干预，如盆底肌训练、饮食指导
                    - 必要时进行多学科会诊
                    - 制定个性化管理方案
                    """)
                else:
                    st.markdown("""
                    **建议**: 
                    - 您可能存在术后肠道功能异常的风险
                    - 请与主治医生进一步沟通，制定个性化的康复计划
                    - 遵循医嘱进行康复训练和饮食调整
                    - 定期复查，密切关注身体状况变化
                    - 保持积极心态，LARS症状大多可以通过适当管理得到改善
                    """)
            else:
                st.info("❌ 预测结果：无明显风险")
                if user_type == "👨‍⚕️ 医护工作者":
                    st.markdown("""
                    **临床建议**: 
                    - 常规术后管理，继续保持观察
                    - 提供健康教育，预防LARS发生
                    - 鼓励健康生活方式，包括合理饮食和适当运动
                    """)
                else:
                    st.markdown("""
                    **建议**: 
                    - 当前评估显示您的风险较低
                    - 请继续保持良好的术后恢复状态
                    - 遵循医嘱进行康复，保持健康生活习惯
                    - 定期体检，关注身体状况
                    - 即使风险较低，仍需注意术后肠道功能变化
                    """)
            
            # 显示输入摘要表格，数值保留两位小数
            summary_data = {
                "特征": ["年龄", "BMI", "肿瘤距离", "手术时间", "排气天数", "肿瘤大小", "TNM 分期", "是否新辅助治疗"],
                "数值": [
                    f"{age:.2f}", f"{BMI:.2f}", f"{tumor_dist:.2f}", 
                    f"{surg_time:.2f}", f"{exhaust:.2f}", f"{tumor_size:.2f}", 
                    f"{TNM:.2f}", f"{neoadjuvant:.2f}"
                ],
                "单位": ["岁", "kg/m²", "cm", "分钟", "天", "cm", "分期数值", "0=否, 1=是"]
            }
            st.markdown("### 输入摘要")
            st.table(pd.DataFrame(summary_data))
                
        except Exception as e:
            st.error(f"预测失败: {str(e)}")
else:
    st.warning("模型未加载，无法进行预测")

# 完成初始化
progress_bar.progress(100)
status_text.text("应用已就绪")
time.sleep(1)
status_text.empty()
progress_bar.empty()

# 使用说明
st.sidebar.markdown("---")
st.sidebar.subheader("使用说明")
st.sidebar.info("1. 选择您的身份（医护/患者）\n2. 输入特征值\n3. 点击预测按钮\n4. 查看结果")

# 添加关于LARS的更多信息
with st.expander("了解更多关于LARS的信息"):
    if user_type == "👨‍⚕️ 医护工作者":
        st.markdown("""
        ### 低位前切除综合征 (LARS) - 基于2025版中国专家共识
        
        **最新定义（2025版中国专家共识）**: 
        LARS是直肠癌患者保肛术后常见的肠道功能障碍症候群，以储便与排空功能障碍为特征，已成为影响患者术后生活质量与临床结局的重要因素。
        
        **临床表现特征**:
        - **发生率高**: 直肠癌保肛术后高达60%~90%的患者会出现不同程度的肠功能障碍
        - **核心症状**: 大便失禁（20%~80%）、排便急迫感（30%~90%）、排空困难（30%~70%）及排便疼痛（20%~50%）
        - **长期影响**: 部分患者术后5年甚至15年仍持续存在LARS症状，严重影响生活质量
        
        **临床分型（基于症状特征）**:
        1. **催促障碍型**: 以大便失禁、排便急迫感和排便频次增加为主要表现
        2. **排空障碍型**: 以排便费力、排便不尽感以及需手助排便等为主要表现
        3. **混合障碍型**: 兼具催促与排空障碍症状
        
        **国际共识核心要素（2020年德尔菲调查法）**:
        - **8项症状指标**: 多变且不可预测的肠道功能改变、粪便性状改变、排便频次增加、反复发作的排便疼痛、排空困难、排便急迫感、大便失禁、漏粪
        - **8项结局指标**: 卫生间依赖、过度关注肠道功能、对肠道功能不满意、需采用应对策略、影响心理健康、影响社交活动、影响亲密关系、影响社会角色
        
        **病理生理机制**:
        1. **新直肠功能障碍**: 储便容量减少、顺应性下降、结肠传输加速
        2. **肛门括约肌功能受损**: 内括约肌神经支配损伤、ISR手术影响
        3. **自主神经损伤**: 上腹下神经丛损伤导致胃肠反射增强
        4. **放疗相关损伤**: 肠黏膜及神经丛损伤、组织纤维化
        5. **转流性造口影响**: 转流性肠炎、细菌定植异常
        
        **阶梯式分级治疗策略（MANUEL欧洲指南推荐）**:
        - **一线治疗**: 最佳支持治疗（饮食调整+药物治疗+盆底功能康复）
        - **二线治疗**: 经肛灌洗、经皮胫神经刺激、针灸等非手术干预
        - **三线治疗**: 骶神经调节、顺行结肠灌洗
        - **最终选择**: 永久性肠造口（其他治疗无效时）
    else:
         st.markdown("""
        ### 什么是LARS（低位前切除综合征）？
        
        **最新专家共识定义**:
        LARS是直肠癌保肛手术后出现的一组肠道功能变化，这些症状会影响患者的日常生活质量和心理健康。
        
        **主要表现**:
        - **肠道症状**: 排便次数增多、急需上厕所、偶尔失控、排便困难等
        - **生活影响**: 需要频繁找厕所、担心肠道问题、影响日常活动和情绪状态
        
        **为什么会发生LARS？**
        - 手术后直肠变短，储存粪便能力下降
        - 控制排便的肌肉和神经在手术中可能受到影响
        - 放疗和造口等因素也会影响肠道功能恢复
        - 每个人的恢复情况不同，症状严重程度也有差异
        
        **国际推荐的管理方法**:
        1. **基础调整**: 饮食控制、规律作息、定时排便训练
        2. **药物治疗**: 医生会根据症状开具相应药物
        3. **康复训练**: 盆底肌锻炼有助于改善控制能力
        4. **专业治疗**: 严重病例可考虑灌洗、神经调节等先进方法
        5. **心理支持**: 保持积极心态，寻求家人和医护人员支持
        
        **重要提示**: 
        LARS是直肠癌术后常见的功能改变，不是手术失败的表现。大多数患者可以通过适当的管理方法使症状得到改善。
        
        **专家建议**:
        - 术后要定期随访，及时向医生反映症状变化
        - 建立健康的生活习惯和排便规律
        - 不要因为尴尬而回避讨论肠道功能问题
        - 严重影响生活时要主动寻求专业帮助

        """)
