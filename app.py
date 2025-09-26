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
    - BMI: 身体质量指数，反映营养与肥胖状况
    - 肿瘤距离: 肿瘤下缘距肛缘距离，影响手术方式
    - 手术时间: 手术持续时间，时间长可能增加组织创伤
    - 排气天数: 术后首次排气时间，反映肠道功能恢复
    - 肿瘤大小: 肿瘤最大直径或体积（长×宽），影响手术复杂度
    - TNM 分期: 肿瘤临床分期，影响术后恢复与并发症风险（详见下方TNM分期转化说明）
    - 是否新辅助治疗: 术前是否接受放化疗，可能影响肠道功能
    """)
    
    # 添加TNM分期转化说明
    with st.sidebar.expander("TNM分期转化说明"):
        st.markdown("""
        **TNM分期与数值对应关系**:
        - 0期 (原位癌): 0
        - I期 (T1-2N0M0): 1
        - II期 (T3-4N0M0): 2
        - III期 (任何T, N1-2M0): 3
        - IV期 (任何T, 任何N, M1): 4
        
        **TNM分期组成**:
        - T (肿瘤): T1-4，数字越大表示肿瘤侵犯越深
        - N (淋巴结): N0-2，数字越大表示淋巴结转移越多
        - M (远处转移): M0无远处转移，M1有远处转移
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
        ### 低位前切除综合征 (LARS)
        
        **定义**: 直肠癌低位前切除术后出现的排便功能障碍综合征，包括排便频率增加、 urgency、失禁等。
        
        **发生机制**:
        - 直肠储袋功能丧失
        - 肛门括约肌损伤
        - 神经损伤
        - 肠道菌群改变
        
        **临床分型**:
        - 轻度LARS: 症状轻微，对生活质量影响小
        - 重度LARS: 症状显著，严重影响生活质量
        
        **管理策略**:
        - 药物治疗: 止泻药、便秘药等对症处理
        - 饮食调整: 低渣饮食、规律进食
        - 盆底康复: 生物反馈、盆底肌训练
        - 手术治疗: 严重病例可考虑造口术
        
        ### 肿瘤大小说明
        肿瘤大小通常指肿瘤的最大直径，或通过长×宽计算得出的近似体积。
        较大的肿瘤可能增加手术难度和术后并发症风险。
        
        ### TNM分期详细说明
        **T (原发肿瘤)**:
        - Tx: 原发肿瘤无法评估
        - T0: 无原发肿瘤证据
        - Tis: 原位癌
        - T1: 肿瘤侵犯粘膜下层
        - T2: 肿瘤侵犯固有肌层
        - T3: 肿瘤穿透固有肌层到达浆膜下层或侵犯无腹膜覆盖的结直肠周围组织
        - T4: 肿瘤穿透脏层腹膜和/或直接侵犯其他器官或结构
        
        **N (区域淋巴结)**:
        - Nx: 区域淋巴结无法评估
        - N0: 无区域淋巴结转移
        - N1: 1-3枚区域淋巴结转移
        - N2: ≥4枚区域淋巴结转移
        
        **M (远处转移)**:
        - M0: 无远处转移
        - M1: 有远处转移
        
        **分期组合**:
        - 0期: TisN0M0
        - I期: T1-2N0M0
        - II期: T3-4N0M0
        - III期: 任何T, N1-2M0
        - IV期: 任何T, 任何N, M1
        """)
    else:
        st.markdown("""
        ### 什么是LARS（低位前切除综合征）？
        
        直肠癌手术后，部分患者可能会出现肠道功能异常，医学上称为"低位前切除综合征"(LARS)。
        
        **常见症状包括**:
        - 排便次数增多（一天多次）
        - 急需排便的感觉（紧迫感，难以控制）
        - 排便失禁（偶尔或经常无法控制排便）
        - 排便不尽感（总觉得没排干净）
        - 便秘与腹泻交替出现
        
        **为什么会发生LARS？**
        - 手术后直肠储存粪便的能力下降
        - 控制排便的肌肉和神经可能受到影响
        - 肠道菌群可能发生变化
        - 手术改变了肠道的正常解剖结构
        
        **如何应对LARS？**
        - 饮食调整：少食多餐，避免高纤维、油腻食物
        - 定时排便：培养规律的排便习惯
        - 盆底肌训练：增强控制排便的肌肉力量
        - 药物治疗：医生可能会开具控制腹泻或便秘的药物
        - 心理支持：保持积极心态，寻求家人和医护人员的支持
        
        **重要提示**：LARS症状通常在术后几个月内最为明显，随后会逐渐改善。大多数患者可以通过适当的自我管理和医疗干预获得较好的生活质量。
        """)
